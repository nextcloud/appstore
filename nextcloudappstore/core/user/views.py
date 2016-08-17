from allauth.account.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App


class AccountView(LoginRequiredMixin, TemplateView):
    """Display and allow changing of the user's names and email address."""
    template_name = 'user/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MyAppsView(LoginRequiredMixin, ListView):
    """List the user's apps."""
    template_name = 'user/my_apps.html'
    model = App

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API Token."""
    template_name = 'user/api_token.html'


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""
    template_name = 'user/password.html'
    success_url = reverse_lazy('user-password')
