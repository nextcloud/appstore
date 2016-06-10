from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

########################################################################
class RegistrationFormRecaptcha(RegistrationFormUniqueEmail):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()

    def clean(self):
        self._validate_unique = True
        super().clean()