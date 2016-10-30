from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.utils.translation import ugettext_lazy as _

from nextcloudappstore.core.models import AppOwnershipTransfer
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


class AppOwnershipTransferView(LoginRequiredMixin, ListView):
    model = AppOwnershipTransfer
    template_name = 'user/app-ownership-transfer.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        transfer_id = request.POST.get('transfer-id', '')
        op = request.POST.get('op', '')
        user = request.user

        if transfer_id and op:
            transfer = self.model.objects.get(id=transfer_id)
            if op == 'commit' and user == transfer.to_user:
                transfer.commit()
                messages.success(request, _('App ownership transferred.'))
            elif op == 'delete' \
                and (user == transfer.to_user
                     or user == transfer.from_user):
                transfer.delete()
                messages.success(
                    request, _('App ownership transfer canceled.'))
        else:
            messages.error(
                request, _('Operation failed.'), extra_tags='danger')

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc_page'] = 'app-ownership-transfer'
        return context
