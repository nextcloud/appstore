from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from nextcloudappstore.core.user.forms import DeleteAccountForm, AccountForm


class ChangeLanguageView(LoginRequiredMixin, TemplateView):
    template_name = 'user/set-language.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'account-change-language'
        return context


class DeleteAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'user/delete-account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteAccountForm()
        context['acc_page'] = 'delete-account'
        return context

    def post(self, request, *args, **kwargs):
        form = DeleteAccountForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.delete()
            return redirect(reverse_lazy('home'))
        else:
            return render(request, self.template_name, {'form': form})


class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name."""

    template_name = 'user/account.html'
    template_name_suffix = ''
    form_class = AccountForm
    success_url = reverse_lazy('user:account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context

    def form_valid(self, form):
        email = EmailAddress.objects.get_primary(user=self.request.user)
        email.email = form.cleaned_data['email']
        email.save()
        messages.success(self.request, 'Account details saved.')
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""

    template_name = 'user/password.html'
    success_url = reverse_lazy('user:account-password')

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
