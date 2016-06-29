from django import forms

from captcha.fields import ReCaptchaField
from rest_framework.authtoken.models import Token

class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()

    def signup(self, request, user):
        t = Token.objects.create(user=user)
        t.save()
