from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from nextcloudappstore.core.models import App
from nextcloudappstore.user.forms import AccountForm, DeleteAccountForm


class IntegrationsView(LoginRequiredMixin, TemplateView):
    template_name = "user/integrations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(owner=self.request.user).filter(Q(is_integration=True) & Q(approved=True))
        if self.request.user.is_superuser:
            context["pending"] = App.objects.filter(is_integration=True).filter(approved=False)
        context["acc_page"] = "account-integrations"
        return context


class TransferAppsView(LoginRequiredMixin, TemplateView):
    template_name = "user/transfer-apps.html"

    def post(self, request, pk):
        app = get_object_or_404(App, pk=pk, owner=self.request.user)
        app.ownership_transfer_enabled = not app.ownership_transfer_enabled
        app.save()
        return redirect(reverse("user:account-transfer-apps"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(owner=self.request.user)
        context["acc_page"] = "account-transfer-apps"
        return context


class ChangeLanguageView(LoginRequiredMixin, TemplateView):
    template_name = "user/set-language.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "account-change-language"
        return context


class DeleteAccountView(LoginRequiredMixin, TemplateView):
    template_name = "user/delete-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = DeleteAccountForm()
        context["acc_page"] = "delete-account"
        return context

    def post(self, request, *args, **kwargs):
        form = DeleteAccountForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        request.user.delete()
        return redirect(reverse_lazy("home"))


class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name."""

    template_name = "user/account.html"
    template_name_suffix = ""
    form_class = AccountForm
    success_url = reverse_lazy("user:account")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "account"
        return context

    def form_invalid(self, form):
        failed_attempts = self.request.session.get("account_update_failed_count", 0)
        if failed_attempts >= 15:
            logout(self.request)
            return HttpResponseRedirect("/")
        self.request.session["account_update_failed_count"] = failed_attempts + 1
        return super().form_invalid(form)

    def form_valid(self, form):
        email = EmailAddress.objects.get_primary(user=self.request.user)
        if email.email != form.cleaned_data["email"]:
            email.email = form.cleaned_data["email"]
            email.save(update_fields=["email"])
        messages.success(self.request, "Account details saved.")
        self.request.session["account_update_failed_count"] = 0
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""

    template_name = "user/password.html"
    success_url = reverse_lazy("user:account-password")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "password"
        return context


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API token, and allow it to be regenerated."""

    template_name = "user/api-token.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "api-token"
        return context
