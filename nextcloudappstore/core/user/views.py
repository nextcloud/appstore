from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic import UpdateView


class DeleteAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'user/delete-account.html'

    def post(self, request, *args, **kwargs):
        self.request.user.delete()
        return redirect(reverse_lazy('home'))


class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name."""

    template_name = 'user/account.html'
    template_name_suffix = ''
    model = User
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Name saved.')
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user


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
