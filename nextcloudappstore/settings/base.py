"""
Django settings for nextcloudappstore project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from os.path import dirname, abspath, join, pardir, realpath

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf.global_settings import LANGUAGES

BASE_DIR = realpath(join(dirname(dirname(abspath(__file__))), pardir))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'nextcloudappstore.core.apps.CoreConfig',
    'nextcloudappstore.core.user.apps.UserConfig',
    'parler',
    'captcha',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'csp.middleware.CSPMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'nextcloudappstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nextcloudappstore.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(BASE_DIR, 'db.sqlite3'),
        'TEST': {
            'NAME': join(BASE_DIR, 'test.sqlite3'),
        }
    }
}

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'app_upload': '100/day',
        'app_register': '100/day',
    }
}

SITE_ID = 1

# Allauth configuration
# http://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_FORM_CLASS = \
    'nextcloudappstore.core.user.forms.SignupFormRecaptcha'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

EXCLUDED_LANGS = ('en-au', 'en-gb')
LANGUAGES = [lang for lang in LANGUAGES if lang[0] not in EXCLUDED_LANGS]
PARLER_LANGUAGES = {
    1: [{'code': code} for code, trans in LANGUAGES],
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
MEDIA_ROOT = join(BASE_DIR, 'media')
RELEASE_DOWNLOAD_ROOT = None
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Default security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'if-none-match',
)
CORS_EXPOSE_HEADERS = (
    'etag',
    'x-content-type-options',
    'content-type',
)
CSP_DEFAULT_SRC = ('\'none\'',)
CSP_IMG_SRC = ('*',)
CSP_FONT_SRC = ('\'self\'',)
CSP_SCRIPT_SRC = ('\'self\'',)
CSP_CONNECT_SRC = ('\'self\'',)
CSP_STYLE_SRC = ('\'self\'',)
CSP_FORM_ACTION = ('\'self\'',)

# use modern no Captcha reCaptcha
NOCAPTCHA = True

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'account_login'

PLATFORM_VERSIONS = ['9', '10', '11']

LOG_LEVEL = 'WARNING'
LOG_FILE = join(BASE_DIR, 'appstore.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

# minimum number of comments to calculate a rating
RATING_THRESHOLD = 5

# number of days to include from today in the recent ratings calculation
RATING_RECENT_DAY_RANGE = 90

LOCALE_PATHS = (
    join(BASE_DIR, 'locale/'),
)
