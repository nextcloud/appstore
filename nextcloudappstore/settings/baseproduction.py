# recommended default settings to inherit in a production environment
from nextcloudappstore.settings.base import *

# DEBUG must be false to not leak sensitive content
DEBUG = False

# The following lines are HTTPS only!
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
CSP_IMG_SRC = ('https:',)

LOG_LEVEL = 'ERROR'
LOGGING['handlers']['file']['filename'] = LOG_FILE
LOGGING['handlers']['file']['level'] = LOG_LEVEL
LOGGING['loggers']['django']['level'] = LOG_LEVEL
