from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AccountView(LoginRequiredMixin, TemplateView):
    """Display and allow changing of the user's name."""
    template_name = 'user/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context


class PasswordView(LoginRequiredMixin, TemplateView):
    """Allow the user to change their password."""
    template_name = 'user/password.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordView, self).get_context_data(**kwargs)
        context['acc_page'] = 'password'
        return context


class APITokenView(LoginRequiredMixin, TemplateView):
    """Allow the user to change their password."""
    template_name = 'user/api-token.html'

    def get_context_data(self, **kwargs):
        context = super(APITokenView, self).get_context_data(**kwargs)
        context['acc_page'] = 'api-token'
        return context
