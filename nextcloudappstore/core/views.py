from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App, Category
from django.http import Http404
from django.db.models import Q


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

    def get_queryset(self):
        category_id = self.kwargs['id']
        queryset = super().get_queryset()

        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        if self.has_search_terms():
            query = None

            for term in self.get_search_terms():
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
        if self.has_search_terms():
            context['search'] = self.get_search_terms()
        return context

    def has_search_terms(self):
        return ('search' in self.request.GET) \
                and self.request.GET['search'].strip()

    def get_search_terms(self):
        return self.request.GET['search'].strip().split()
