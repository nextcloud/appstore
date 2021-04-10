from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import filter_users_by_email, user_username, \
    user_pk_to_url_str
from django import forms
from django.contrib.auth import get_user_model
from django.forms import EmailField, CharField, PasswordInput
from django.utils.translation import ugettext_lazy as _
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget


class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField(widget=ReCaptchaWidget())
    first_name = CharField(max_length=30, label=_('First name'))
    last_name = CharField(max_length=30, label=_('Last name'))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class DeleteAccountForm(forms.Form):
    email = EmailField(required=True, label=_('Your email address'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and self.user.email == email:
            return email
        else:
            raise forms.ValidationError(_(
                'The given email address does not match your email address'))


class AccountForm(forms.ModelForm):
    passwd = CharField(widget=PasswordInput(), label=_('Confirm password'),
                       help_text=_('Password is required to prevent '
                                   'unauthorized users from changing your '
                                   'email address and resetting your '
                                   'password. This field does not update your '
                                   'password!'))

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        value = self.cleaned_data['email']
        users = filter_users_by_email(value)
        if [u for u in users if u.pk != self.instance.pk]:
            msg = _(
                'This email address is already associated with another '
                'account.')
            raise forms.ValidationError(msg)
        return value

    def clean_passwd(self):
        value = self.cleaned_data['passwd']
        if self.instance.check_password(value):
            return value
        else:
            raise forms.ValidationError(_('Invalid password'))


class CustomResetPasswordForm(forms.Form):
    # remove this class once issue #1307 is resolved django-allauth
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.TextInput(attrs={
            "type": "email",
            "size": "30",
            "placeholder": _("Email address"),
        })
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
            path = reverse("account_reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            from allauth.utils import build_absolute_uri
            url = build_absolute_uri(
                request, path)

            context = {"current_site": current_site,
                       "user": user,
                       "password_reset_url": url,
                       "request": request}

            from allauth.account import app_settings

            if app_settings.AUTHENTICATION_METHOD \
                    != app_settings.AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            from allauth.account.adapter import get_adapter
            get_adapter(request).send_mail(
                'account/email/password_reset_key',
                email,
                context)
        return self.cleaned_data["email"]
