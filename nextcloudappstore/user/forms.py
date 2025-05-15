"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import (
    filter_users_by_email,
    user_pk_to_url_str,
    user_username,
)
from allauth.socialaccount.models import SocialAccount
from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.forms import CharField, EmailField, PasswordInput
from django.utils.translation import gettext_lazy as _


class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""

    captcha = CaptchaField()
    first_name = CharField(max_length=30, label=_("First name"))
    last_name = CharField(max_length=30, label=_("Last name"))
    subscribe_to_news = forms.BooleanField(
        label=_("I would like to receive app developer news and updates from Nextcloud by email"),
        required=False,
        initial=False,
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Set the subscription preference on the user's profile
        user.profile.subscribe_to_news = self.cleaned_data["subscribe_to_news"]
        user.profile.save()


class DeleteAccountForm(forms.Form):
    email = EmailField(required=True, label=_("Your email address"))
    passwd = CharField(
        required=False,
        widget=PasswordInput(),
        label=_("Your password"),
        help_text=_("*Required if the account is registered with a password"),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.user and self.user.email == email:
            return email
        raise forms.ValidationError(_("The given email address does not match your email address"))

    def clean_passwd(self):
        passwd = self.cleaned_data.get("passwd")
        if self.user:
            social_user = SocialAccount.objects.filter(user_id=self.user, provider="github").first()
            if social_user is not None or self.user.check_password(passwd):
                return passwd
        raise forms.ValidationError(_("Invalid password"))


class AccountForm(forms.ModelForm):
    passwd = CharField(
        widget=PasswordInput(),
        label=_("Confirm password"),
        help_text=_(
            "Required when changing your First Name, Last Name, or "
            "Email Address to prevent unauthorized changes to critical account details. "
            "This field does not update your password!"
        ),
        required=False,
    )
    subscribe_to_news = forms.BooleanField(
        label=_("I would like to receive app developer news and updates from Nextcloud by email"),
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        # Set initial value of subscribe_to_news based on user's profile
        if self.user and hasattr(self.user, "profile"):
            self.fields["subscribe_to_news"].initial = self.user.profile.subscribe_to_news

    def clean_email(self):
        value = self.cleaned_data["email"]
        users = filter_users_by_email(value)
        if [u for u in users if u.pk != self.instance.pk]:
            msg = _("This email address is already associated with another account.")
            raise forms.ValidationError(msg)
        return value

    def clean_passwd(self):
        value = self.cleaned_data.get("passwd")
        # If password was entered, validate it
        if value and not self.instance.check_password(value):
            raise forms.ValidationError(_("Invalid password"))
        return value

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        subscribe_to_news = cleaned_data.get("subscribe_to_news")

        changed_fields = []
        if self.user:
            if email and email != self.user.email:
                changed_fields.append("email")
            if first_name and first_name != self.user.first_name:
                changed_fields.append("first_name")
            if last_name and last_name != self.user.last_name:
                changed_fields.append("last_name")
            if (
                hasattr(self.user, "profile")
                and subscribe_to_news is not None
                and subscribe_to_news != self.user.profile.subscribe_to_news
            ):
                changed_fields.append("subscribe_to_news")

        if not changed_fields:
            return cleaned_data

        # If the only changed field is subscribe_to_news, we do not require password
        if changed_fields == ["subscribe_to_news"]:
            # Remove password-related errors if they exist
            if "passwd" in self._errors:
                del self._errors["passwd"]

        else:
            # If critical fields (email, first_name, last_name) changed,
            # ensure password was provided and is correct.
            # If no password provided or invalid, an error would be present from clean_passwd().
            # Ensure that passwd was actually provided and is valid.
            if not cleaned_data.get("passwd"):
                self.add_error("passwd", _("Password is required to change these fields."))

        return cleaned_data


class CustomResetPasswordForm(forms.Form):
    # remove this class once issue #1307 is resolved django-allauth
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "size": "30",
                "placeholder": _("Email address"),
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        from allauth.account.adapter import get_adapter

        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True)

        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        from django.contrib.sites.shortcuts import get_current_site

        current_site = get_current_site(request)
        email = self.cleaned_data["email"]
        token_generator = EmailAwarePasswordResetTokenGenerator()

        for user in self.users:
            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            from django.urls import reverse

            path = reverse(
                "account_reset_password_from_key", kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key)
            )
            from allauth.utils import build_absolute_uri

            url = build_absolute_uri(request, path)

            context = {"current_site": current_site, "user": user, "password_reset_url": url, "request": request}

            from allauth.account import app_settings

            if app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.EMAIL:
                context["username"] = user_username(user)
            from allauth.account.adapter import get_adapter

            get_adapter(request).send_mail("account/email/password_reset_key", email, context)
        return self.cleaned_data["email"]
