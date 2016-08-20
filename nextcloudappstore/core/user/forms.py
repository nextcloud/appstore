from django import forms

from captcha.fields import ReCaptchaField


class SignupFormRecaptcha(forms.Form):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()

    def signup(self, request, user):
        pass
