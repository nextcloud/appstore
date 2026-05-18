"""
SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from allauth.core import ratelimit
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, UpdateView

from nextcloudappstore.core.models import App, AppRating
from nextcloudappstore.user.forms import AccountForm, DeleteAccountForm


@method_decorator(never_cache, name="dispatch")
class IntegrationsView(LoginRequiredMixin, TemplateView):
    template_name = "user/integrations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(owner=self.request.user).filter(Q(is_integration=True) & Q(approved=True))
        if self.request.user.is_superuser:
            context["pending"] = App.objects.filter(is_integration=True).filter(approved=False)
        context["acc_page"] = "account-integrations"
        return context


@method_decorator(never_cache, name="dispatch")
class TransferAppsView(LoginRequiredMixin, TemplateView):
    template_name = "user/transfer-apps.html"

    def post(self, request, pk):
        app = get_object_or_404(App, pk=pk, owner=self.request.user)
        if "transfer" in request.path:
            app.ownership_transfer_enabled = not app.ownership_transfer_enabled
        if "orphan" in request.path:
            app.is_orphan = not app.is_orphan
        app.save()
        return redirect(reverse("user:account-transfer-apps"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(owner=self.request.user)
        context["acc_page"] = "account-transfer-apps"
        return context


@method_decorator(never_cache, name="dispatch")
class EnterpriseAppsView(LoginRequiredMixin, TemplateView):
    template_name = "user/enterprise-apps.html"

    def post(self, request, pk):
        app = get_object_or_404(App, pk=pk, owner=self.request.user)
        app.is_enterprise_supported = not app.is_enterprise_supported
        app.save()
        return redirect(reverse("user:account-enterprise-apps"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(owner=self.request.user)
        context["acc_page"] = "account-enterprise-apps"
        return context


@method_decorator(never_cache, name="dispatch")
class ChangeLanguageView(LoginRequiredMixin, TemplateView):
    template_name = "user/set-language.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "account-change-language"
        return context


@method_decorator(never_cache, name="dispatch")
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


@method_decorator(never_cache, name="dispatch")
class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name and subscription."""

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
        user = self.request.user
        # Compare case-insensitively: allauth stores EmailAddress.email lowercased
        # and add_email() also lowercases. A case-only "change" is a no-op there,
        # so it must not consume the rate-limit budget either.
        current_email = EmailAddress.objects.get_primary(user=user).email
        new_email = form.cleaned_data["email"]
        email_changed = new_email.lower() != current_email.lower()

        if email_changed and not ratelimit.consume(self.request, action="manage_email"):
            # Persist name/subscription changes but skip the email change and
            # surface an inline error. User.email is intentionally not updated.
            # Construct_instance set user.email to the rejected new email in
            # memory; refresh it so the profile pre_save signal handler
            # (signals.handle_subscription_change) does not leak that value to
            # Odoo via instance.user.email when subscribe_to_news flips.
            user.refresh_from_db(fields=["email"])
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save(update_fields=["first_name", "last_name"])
            user.profile.subscribe_to_news = form.cleaned_data["subscribe_to_news"]
            user.profile.save(update_fields=["subscribe_to_news"])
            form.add_error("email", _("Too many email change attempts. Please try again later."))
            self.request.session["account_update_failed_count"] = 0
            return self.render_to_response(self.get_context_data(form=form))

        message = "Account details saved."
        if email_changed:
            # Delete other unconfirmed email addresses
            EmailAddress.objects.filter(user=user).exclude(primary=True).delete()
            # Add new email address, send confirmation email
            EmailAddress.objects.add_email(self.request, user, new_email, confirm=True)
            message += f" Please verify your email address from the confirmation email sent to {new_email}."

        # Update subscription preference
        user.profile.subscribe_to_news = form.cleaned_data["subscribe_to_news"]
        user.profile.save()

        messages.success(self.request, message)
        self.request.session["account_update_failed_count"] = 0
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(never_cache, name="dispatch")
class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""

    template_name = "user/password.html"
    success_url = reverse_lazy("user:account-password")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "password"
        return context


@method_decorator(never_cache, name="dispatch")
class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API token, and allow it to be regenerated."""

    template_name = "user/api-token.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["acc_page"] = "api-token"
        return context


@method_decorator(never_cache, name="dispatch")
class AppealCommentsView(LoginRequiredMixin, TemplateView):
    template_name = "user/appeal-comments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            # context["pending"] = AppRating.objects.filter(appeal=True)
            pending_ratings = AppRating.objects.filter(appeal=True)
            pending_with_lang = [
                {
                    "rating": rating,
                    "lang": rating.translations.first().language_code if rating.translations.exists() else None,
                }
                for rating in pending_ratings
            ]
            context["pending"] = pending_with_lang
        context["acc_page"] = "appeal-comments"
        return context
