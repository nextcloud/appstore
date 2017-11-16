from allauth.account.utils import filter_users_by_email
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
                'This e-mail address is already associated with another '
                'account.')
            raise forms.ValidationError(msg)
        return value

    def clean_passwd(self):
        value = self.cleaned_data['passwd']
        if self.instance.check_password(value):
            return value
        else:
            raise forms.ValidationError(_('Invalid password'))
