from nextcloudappstore.settings.base import *

DEBUG = True
SECRET_KEY = 'secret'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
RECAPTCHA_PUBLIC_KEY = '<RECAPTCHA_PUBLIC_KEY>'
RECAPTCHA_PRIVATE_KEY = '<RECAPTCHA_PRIVATE_KEY>'
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'Appstore <appstore@nextcloud.com>'
INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
