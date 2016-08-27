from django import forms
from captcha.fields import ReCaptchaField
from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _


class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()

    def signup(self, request, user):
        pass


class DeleteAccountForm(forms.Form):
    email = EmailField(required=True, label=_('Your e-mail address'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and self.user.email == email:
            return email
        else:
            raise forms.ValidationError(_(
                'The given e-mail address does not match your e-mail address'))
