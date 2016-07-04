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

    def get_queryset(self, request):
        category_id = self.kwargs['id']
        queryset = super().get_queryset()

        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        if ('search' in request.GET) and request.GET['search'].strip():
            search_words = request.GET['search'].strip().split()
            query = None

            for word in search_words:
                q = Q(translations__name__contains=word) | \
                    Q(translations__description__contains=word)
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
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                    and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(
                    _("Empty list and '%(class_name)s.allow_empty' is False.")
                    % {'class_name': self.__class__.__name__})
        context = self.get_context_data()
        return self.render_to_response(context)
