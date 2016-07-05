from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App, Category
from django.utils.functional import cached_property
from django.utils.translation import get_language, get_language_info


class AppDetailView(DetailView):
    model = App
    template_name = 'app/detail.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryAppListView(ListView):
    model = App
    template_name = 'app/list.html'
    allow_empty = True

    def get_queryset(self):
        lang = get_language_info(get_language())['code']
        category_id = self.kwargs['id']
        queryset = App.search(self.search_terms, lang)
        if category_id:
            return queryset.filter(categories__id=category_id)
        else:
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
