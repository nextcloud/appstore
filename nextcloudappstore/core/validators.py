from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _  # type: ignore


class HttpsUrlValidator(URLValidator):
    message = _('Enter a valid HTTPS URL')

    def __init__(self):
        super().__init__(schemes=['https'])
