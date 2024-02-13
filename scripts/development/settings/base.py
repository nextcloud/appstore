import sys

from nextcloudappstore.settings.base import *

DEBUG = True
SECRET_KEY = "secret"  # nosec
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# this whitelists 127.0.0.1 and localhost
RECAPTCHA_PUBLIC_KEY = "6LcCTyITAAAAABofGcLG2L4QVfXY3Ugs6MQ_UHSO"
RECAPTCHA_PRIVATE_KEY = "6LcCTyITAAAAAB3OT3_HnnzZXOQW4WzNoaNSN-3i"
EMAIL_HOST = "localhost"
DEFAULT_FROM_EMAIL = "Nextcloud App Store <appstore@nextcloud.com>"
INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ("127.0.0.1",)
VALIDATE_CERTIFICATES = False
ACCOUNT_ADAPTER = "nextcloudappstore.user.adapters.CustomAccountAdapter"

FIXTURE_DIRS = (BASE_DIR / "core/tests/e2e/fixtures",)

LOGGING["handlers"]["console"] = {
    "level": LOG_LEVEL,
    "class": "logging.StreamHandler",
}
LOGGING["loggers"]["django"]["handlers"] += ["console"]

# make it possible to run debug toolbar for api
CSP_EXCLUDE_URL_PREFIXES = ("/api/v1",)

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["app_upload"] = "10000/day"
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["app_register"] = "10000/day"

if "test" in sys.argv:
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3"}

# For development, dump email to the console instead of trying to actually send it.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Alternatively, run python3 -m smtpd -n -c DebuggingServer -d '0.0.0.0:2525' and set
# EMAIL_PORT = 2525

EMAIL_HOST = "localhost"
EMAIL_HOST_USER = "noreply@nextcloud.com"

# Disable testing in tests
TESTING = bool(len(sys.argv) > 1 and sys.argv[1] == "test")
CAPTCHA_TEST_MODE = TESTING
