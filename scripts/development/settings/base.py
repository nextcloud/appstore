from nextcloudappstore.settings.base import *

DEBUG = True
SECRET_KEY = 'secret'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
RECAPTCHA_PUBLIC_KEY = '<RECAPTCHA_PUBLIC_KEY>'
RECAPTCHA_PRIVATE_KEY = '<RECAPTCHA_PRIVATE_KEY>'
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'Nextcloud App Store <appstore@nextcloud.com>'
INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ('127.0.0.1',)
VALIDATE_CERTIFICATES = False

FIXTURE_DIRS = (
    join(BASE_DIR, 'nextcloudappstore/core/tests/e2e/fixtures'),
)
