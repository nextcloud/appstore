from django import forms
from captcha.fields import ReCaptchaField
from django.forms import EmailField, CharField
from django.utils.translation import ugettext_lazy as _


class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()
    first_name = CharField(max_length=30, label=_('First name'))
    last_name = CharField(max_length=30, label=_('Last name'))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


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
