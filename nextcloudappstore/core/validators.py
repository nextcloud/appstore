from django.core.validators import URLValidator


class HttpsUrlValidator(URLValidator):
    def __init__(self):
        super().__init__(schemes=['https'])
