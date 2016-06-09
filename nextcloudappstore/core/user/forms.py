from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

########################################################################
class RegistrationFormRecaptcha(RegistrationFormUniqueEmail):
    """integrate a recaptcha field."""
    recaptcha = ReCaptchaField()
