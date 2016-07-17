from functools import reduce
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import get_language, get_language_info
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App, Category


def app_description(request, id):
    app = get_object_or_404(App, id=id)
    return HttpResponse(app.description, content_type='text/plain')


class AppDetailView(DetailView):
    model = App
    template_name = 'app/detail.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['latest_releases_by_platform_v'] = \
            self.object.latest_releases_by_platform_v()
        return context


class AppReleasesView(DetailView):
    model = App
    template_name = 'app/releases.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['releases_by_platform_v'] = \
            self.object.releases_by_platform_v()
        return context


class CategoryAppListView(ListView):
    model = App
    template_name = 'app/list.html'
    allow_empty = True

    def get_queryset(self):
        order_by = self.request.GET.get('order_by', 'last_modified')
        ordering = self.request.GET.get('ordering', 'desc')
        featured = self.request.GET.get('featured', False)
        maintainer = self.request.GET.get('maintainer', False)
        sort_columns = []

        allowed_order_by = {'name', 'last_modified'}
        if order_by in allowed_order_by:
            if order_by == 'name':
                order_by = 'translations__name'
            if ordering == 'desc':
                sort_columns.append('-' + order_by)
            else:
                sort_columns.append(order_by)

        lang = get_language_info(get_language())['code']
        category_id = self.kwargs['id']
        queryset = App.objects.search(self.search_terms, lang).order_by(
            *sort_columns)
        if maintainer:
            try:
                user = User.objects.get_by_natural_key(maintainer)
                queryset = queryset.filter(Q(owner=user) |
                                           Q(co_maintainers=user))
            except ObjectDoesNotExist:
                return queryset.none()
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if featured == "true":
            queryset = queryset.filter(featured=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        category_id = self.kwargs['id']
        if category_id:
            context['current_category'] = Category.objects.get(id=category_id)
        if self.search_terms:
            context['search_query'] = ' '.join(self.search_terms)
        context['url_params'] = self.url_params
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

        search = self._url_params_str('search')
        filters = self._url_params_str('featured', 'maintainer')
        ordering = self._url_params_str('order_by', 'ordering')

        return {
            'search': search,
            'filters': filters,
            'ordering': ordering,
            'search_filters': self._join_url_params_strs(search, filters),
            'filters_ordering': self._join_url_params_strs(filters, ordering),
        }

    def _url_params_str(self, *params):
        args = map(lambda param: (param, self.request.GET.get(param, '')),
                   params)
        present_args = filter(lambda a: a[1], args)
        return urlencode(dict(present_args))

    def _join_url_params_strs(self, *strings):
        return '&'.join(strings).lstrip('&')

    @cached_property
    def search_terms(self):
        return self.request.GET.get('search', '').strip().split()
