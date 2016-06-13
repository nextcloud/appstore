from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from nextcloudappstore.core.mixins \
     import CategoryContextMixin, RecommendedAppsContextMixin
from nextcloudappstore.core.models import App, Category


class HomeView(CategoryContextMixin,
               RecommendedAppsContextMixin, TemplateView):
    template_name = "home.html"


class AppDetailView(CategoryContextMixin, DetailView):
    model = App
    template_name = 'app/detail.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'


class AppListView(CategoryContextMixin, ListView):
    model = App
    template_name = 'app/list.html'


class AppsByCategoryView(AppListView):
    def get_queryset(self):
        return super().get_queryset().filter(categories=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = Category.objects.get(
            id=self.kwargs['id'])
        return context
