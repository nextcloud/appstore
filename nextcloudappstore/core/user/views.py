from allauth.account.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView


class AccountView(LoginRequiredMixin, TemplateView):
    """Display and allow changing of the user's name."""

    template_name = 'user/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""

    template_name = 'user/password.html'
    success_url = reverse_lazy('account-password')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'password'
        return context


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API token, and allow it to be regenerated."""

    template_name = 'user/api-token.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'api-token'
        return context
