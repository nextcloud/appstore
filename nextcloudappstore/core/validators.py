import re
from urllib.parse import unquote, urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _  # type: ignore


class HttpsUrlValidator(URLValidator):
    message = _("Enter a valid HTTPS URL")

    def __init__(self):
        super().__init__(schemes=["https"])

    def __call__(self, value):
        # 1. Let Django's built-in URL checks run
        super().__call__(value)

        decoded_url = unquote(value)
        parsed_url = urlparse(decoded_url)

        # 2. Check for control characters:
        # Null(\x00), Tab(\x09), Newline(\x0A), Carriage Return(\x0D), Escape(\x1B),DEL (\x7F)
        if re.search(r"[\x00-\x1F\x7F]", decoded_url):
            raise ValidationError(_("URL contains invalid (control) characters."))

        # 3. Early enforcing of a .tar.gz extension
        if not parsed_url.path.endswith(".tar.gz"):
            raise ValidationError(_("URL must end with .tar.gz"))
