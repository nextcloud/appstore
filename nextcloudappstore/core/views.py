from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App, Category
from django.db.models import Q
from django.utils.functional import cached_property


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
        category_id = self.kwargs['id']
        queryset = super().get_queryset()

        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        if self.search_terms:
            query = None

            for term in self.search_terms:
                q = Q(translations__name__contains=term) | \
                    Q(translations__description__contains=term)
                if query is None:
                    query = q
                else:
                    query = query | q

            queryset = queryset.filter(query)

            # Remove duplicates that for some reason sometimes occur
            queryset = list(set(queryset))

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
        if ('search' in self.request.GET) \
                and self.request.GET['search'].strip():
            return self.request.GET['search'].strip().split()
        else:
            return []
