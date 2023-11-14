from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.utils.translation import get_language, get_language_info
from django.views.decorators.http import etag
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework.generics import ListAPIView
from semantic_version import Version

from nextcloudappstore.core.caching import app_etag
from nextcloudappstore.core.facades import flatmap
from nextcloudappstore.core.forms import (
    AppRatingForm,
    AppRegisterForm,
    AppReleaseUploadForm,
)
from nextcloudappstore.core.models import App, AppRating, Category, Podcast
from nextcloudappstore.core.serializers import AppRatingSerializer
from nextcloudappstore.core.versioning import pad_min_version


@etag(app_etag)
def app_description(request, id):
    app = get_object_or_404(App, id=id)
    return HttpResponse(app.description, content_type="text/plain")


class AppRatingApi(ListAPIView):
    serializer_class = AppRatingSerializer

    def get_queryset(self):
        id = self.kwargs.get("id")
        lang = self.request.GET.get("lang", self.request.LANGUAGE_CODE)
        app = get_object_or_404(App, id=id)
        queryset = AppRating.objects.language(lang).filter(app=app)

        current_user = self.request.GET.get("current_user", "false")
        if current_user == "true":
            return queryset.filter(user=self.request.user)
        else:
            return queryset


class AppDetailView(DetailView):
    queryset = App.objects.prefetch_related(
        "releases",
        "screenshots",
        "co_maintainers",
        "translations",
    ).select_related("owner")
    template_name = "app/detail.html"
    slug_field = "id"
    slug_url_kwarg = "id"

    def post(self, request, id):
        form = AppRatingForm(request.POST, id=id, user=request.user)
        # there is no way that a rating can be invalid by default
        if form.is_valid() and request.user.is_authenticated:
            form.save()
        return redirect("app-detail", id=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["DISCOURSE_URL"] = settings.DISCOURSE_URL.rstrip("/")
        context["rating_form"] = AppRatingForm(initial={"language_code": get_language()})

        ratings = AppRating.objects.filter(app=context["app"])
        rating_languages = flatmap(lambda r: r.get_available_languages(), ratings)

        # make sure current session language is in the list even if there are
        # no comments.
        rating_languages = list(rating_languages)
        if get_language() not in rating_languages:
            rating_languages.append(get_language())

        context["languages"] = set(sorted(rating_languages))
        context["fallbackLang"] = "en" if "en" in context["languages"] else ""
        context["user_has_rated_app"] = False
        if self.request.user.is_authenticated:
            try:
                app_rating = AppRating.objects.get(user=self.request.user, app=context["app"])

                # if parler falls back to a fallback language
                # it doesn't set the language as current language
                # and we can't select the correct language in the
                # frontend. So we try and find a languge that is
                # available
                language_code = app_rating.get_current_language()
                if not app_rating.has_translation(language_code):
                    for fallback in app_rating.get_fallback_languages():
                        if app_rating.has_translation(fallback):
                            app_rating.set_current_language(fallback)

                # when accessing an empty comment django-parler tries to
                # fall back to the default language. However for comments
                # the default (English) does not always exist. Unfortunately
                # it throws the same exception as non existing models,
                # so we need to access it beforehand
                try:
                    comment = app_rating.comment
                except AppRating.DoesNotExist:
                    comment = ""

                context["rating_form"] = AppRatingForm({
                    "rating": app_rating.rating,
                    "comment": comment,
                    "language_code": app_rating.get_current_language(),
                })
                context["user_has_rated_app"] = True
            except AppRating.DoesNotExist:
                pass
        context["categories"] = Category.objects.prefetch_related("translations").all()
        context["latest_releases_by_platform_v"] = self.object.latest_releases_by_platform_v()
        context["is_integration"] = self.object.is_integration
        return context


class AppReleasesView(DetailView):
    queryset = App.objects.prefetch_related(
        "translations",
        "releases__translations",
        "releases__phpextensiondependencies__php_extension",
        "releases__databasedependencies__database",
        "releases__shell_commands",
        "releases__licenses",
    )
    template_name = "app/releases.html"
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.prefetch_related("translations").all()

        releases = self.object.releases_by_platform_v()
        unstables = self.object.unstable_releases_by_platform_v()
        versions = set(list(releases.keys()) + list(unstables.keys()))
        all_releases = list(map(lambda v: (v, releases.get(v, []) + unstables.get(v, [])), versions))
        context["releases_by_platform_v"] = self._sort_by_platform_v(all_releases)
        return context

    def _sort_by_platform_v(self, releases_by_platform, reverse=True):
        """Sorts a list of tuples like (<platform version>, [releases]) by
        platform version.

        :param releases_by_platform: A list of tuples.
        :param reverse: Descending order if True, ascending otherwise.
        :return sorted list of tuples.
        """

        return sorted(releases_by_platform, reverse=reverse, key=lambda v: Version(pad_min_version(v[0])))


class CategoryAppListView(ListView):
    model = App
    template_name = "app/list.html"
    allow_empty = True

    def get_queryset(self):
        order_by = self.request.GET.get("order_by", "rating_overall")
        ordering = self.request.GET.get("ordering", "desc")
        is_featured = self.request.GET.get("is_featured", False)
        maintainer = self.request.GET.get("maintainer", False)
        sort_columns = []

        if self.kwargs.get("is_featured_category", False):
            is_featured = "true"

        allowed_order_by = {"name", "last_release", "rating_overall", "rating_recent"}
        if order_by in allowed_order_by:
            if order_by == "name":
                order_by = "translations__name"
            if ordering == "desc":
                sort_columns.append("-" + order_by)
            else:
                sort_columns.append(order_by)

        lang = get_language_info(get_language())["code"]
        category_id = self.kwargs["id"]
        queryset = (
            App.objects.search(self.search_terms, lang)
            .order_by(*sort_columns)
            .filter(Q(releases__gt=0) | (Q(is_integration=True) & Q(approved=True)))
        )
        if maintainer:
            try:
                user = User.objects.get_by_natural_key(maintainer)
                queryset = queryset.filter(Q(owner=user) | Q(co_maintainers=user))
            except ObjectDoesNotExist:
                return queryset.none()
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if is_featured == "true":
            queryset = queryset.filter(is_featured=True)
        return queryset.prefetch_related("screenshots", "translations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.prefetch_related("translations").all()
        category_id = self.kwargs["id"]
        context["is_featured_category"] = self.kwargs.get("is_featured_category", False)
        if category_id:
            context["current_category"] = get_object_or_404(Category, id=category_id)
        if self.search_terms:
            context["search_query"] = " ".join(self.search_terms)
        context["url_params"] = self.url_params
        podcast = Podcast.objects.filter(show=True).last()
        if podcast:
            podcast.excerpt = (podcast.excerpt[:230] + "...") if len(podcast.excerpt) > 230 else podcast.excerpt
        if podcast:
            context["podcast"] = podcast
        return context

    @cached_property
    def url_params(self):
        """URL encoded strings with the GET params of the last request.

        Intended for preserving GET params upon clicking a link by including
        one (and only one) of these strings in the "href" attribute.

        The parameters are divided into three groups: search, filters and
        ordering. In addition to these three, the returned dict also contains
        some combinations of them, as specified by the dict keys.

        No leading "?" or "&".

        :return dict with URL encoded strings.
        """

        search = self._url_params_str("search")
        filters = self._url_params_str("is_featured", "maintainer")
        ordering = self._url_params_str("order_by", "ordering")

        return {
            "search": search,
            "filters": filters,
            "ordering": ordering,
            "search_filters": self._join_url_params_strs(search, filters),
            "filters_ordering": self._join_url_params_strs(filters, ordering),
        }

    def _url_params_str(self, *params):
        args = map(lambda param: (param, self.request.GET.get(param, "")), params)
        present_args = filter(lambda a: a[1], args)
        return urlencode(dict(present_args))

    def _join_url_params_strs(self, *strings):
        return "&".join(filter(None, strings))

    @cached_property
    def search_terms(self):
        return self.request.GET.get("search", "").strip().split()


class AppUploadView(LoginRequiredMixin, TemplateView):
    template_name = "app/upload.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AppReleaseUploadForm()
        return context


class AppRegisterView(LoginRequiredMixin, TemplateView):
    template_name = "app/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AppRegisterForm()
        return context
