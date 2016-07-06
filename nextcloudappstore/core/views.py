from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import get_language, get_language_info
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App, Category


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


class CategoryAppListView(ListView):
    model = App
    template_name = 'app/list.html'
    allow_empty = True

    def get_queryset(self):
        order_by = self.request.GET.get('order_by', 'last_modified')
        ordering = self.request.GET.get('ordering', 'desc')
        featured = self.request.GET.get('featured', False)
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
        return context

    @cached_property
    def search_terms(self):
        return self.request.GET.get('search', '').strip().split()
