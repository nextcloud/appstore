from django.shortcuts import render
from django.views.generic.base import TemplateView

from nextcloudappstore.core.mixins import CategoryContextMixin, RecommendedAppsContextMixin

class HomeView(CategoryContextMixin, RecommendedAppsContextMixin, TemplateView):
    template_name = "home.html"
