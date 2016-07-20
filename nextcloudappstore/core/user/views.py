from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from allauth.account import views

from nextcloudappstore.core.models import App


class ProfileView(LoginRequiredMixin, ListView):
    """Display the users profile"""
    template_name = 'user/profile.html'
    model = App

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class ChangeNameView(LoginRequiredMixin, TemplateView):
    """Display the users profile"""
    template_name = 'user/change_name.html'


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the users profile"""
    template_name = 'user/api_token.html'
