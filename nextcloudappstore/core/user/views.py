from allauth.account.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils.translation import get_language_info, get_language
from django.views.generic import TemplateView, UpdateView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App
from django.contrib import messages
from rest_framework.authtoken.models import Token


class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name."""
    template_name = 'user/account.html'
    template_name_suffix = ''
    model = User
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('user-account')

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Name saved.')
        return super(AccountView, self).form_valid(form)

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            return None


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API token, and allow it to be regenerated."""
    template_name = 'user/api_token.html'

    def get_context_data(self, **kwargs):
        context = super(APITokenView, self).get_context_data(**kwargs)
        context['acc_page'] = 'api_token'
        return context


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""
    template_name = 'user/password.html'
    success_url = reverse_lazy('user-password')

    def get_context_data(self, **kwargs):
        context = super(PasswordView, self).get_context_data(**kwargs)
        context['acc_page'] = 'password'
        return context
