Configuration
=============

The store is configured by using a Python file that lets you overwrite base settings and configure required settings. A configuration can set or override any `Django setting <https://docs.djangoproject.com/en/2.1/ref/settings/>`_ or Django plugin setting.

.. _production-configuration:

Production Configuration
------------------------
In order to get up a minimal production configuration you can extend the base production settings which expect your site to run on HTTPS and fill in the remaining bits:

.. note:: Absolutely make sure to generate a new **SECRET_KEY** value! Use the following command for instance to generate a token:

::

    env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo

.. code-block:: python

    from nextcloudappstore.settings.baseproduction import *

    # generate the SECRET_KEY by yourself for instance by using the following command:
    # env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo
    SECRET_KEY = 'CRYPTO: CHANGE THIS VALUE!'

    ALLOWED_HOSTS = ['production-domain.com']

    # Email settings which are used to send mails (e.g. confirm account messages)
    # for more configuration options consult the Django documentation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_HOST
    DEFAULT_FROM_EMAIL = 'appstore@nextcloud.com'
    ADMINS = [('Your Name', 'your-mail@example.com')]
    EMAIL_HOST = 'localhost'

    # postgres or other db if needed if anything other than sqlite is used
    # you need to create the database, user and password first
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'nextcloudappstore',
            'USER': 'nextcloudappstore',
            'PASSWORD': 'password',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

    # Path to where your static content lies (e.g. CSS, JavaScript and images)
    # This should point to a directory served by your web-server
    STATIC_ROOT = '/var/www/production-domain.com/static/'

    # Url for serving content uploaded by users, ideally different domain
    MEDIA_URL = 'https://separate-domain.com/'

    # Path to where user uploaded content lies, should point to a directory
    # served by your web-server
    MEDIA_ROOT = '/var/www/production-domain.com/media/'

    # Public and private keys for Googles recaptcha
    RECAPTCHA_PUBLIC_KEY = 'YOUR PUBLIC KEY'
    RECAPTCHA_PRIVATE_KEY = 'YOUR PRIVATE KEY'

    # Discourse user that is allowed to create categories. This will be used
    # to automatically create categories when registering apps
    DISCOURSE_USER = 'tom'
    DISCOURSE_TOKEN = 'a token'

    #########################
    # Overridable Defaults: #
    #########################

    # Url for serving non user uploaded files like CSS, JavaScript and images
    # STATIC_URL = '/static/'

    # Url or domain for serving user uploaded files
    # MEDIA_URL = '/media/'

    # how many times a user is allowed to call the app upload route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_upload'] = '100/day'
    # how many times a user is allowed to call the app register route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_register'] = '100/day'

    # Only set this parameter if you want to use a different tmp directory for app downloads
    # RELEASE_DOWNLOAD_ROOT = '/other/tmp'

    # Only set if you want a different log location than the one in the main directory
    # Make sure that this appears above the first use
    # LOG_FILE = '/path/to/appstore/appstore.log'

    # minimum number of comments to calculate a rating
    # RATING_THRESHOLD = 5

    # number of days to include from today in the recent ratings calculation
    # RATING_RECENT_DAY_RANGE = 90

    # MAX_DOWNLOAD_FILE_SIZE = 1024 ** 2  # bytes
    # MAX_DOWNLOAD_TIMEOUT = 60  # seconds
    # MAX_DOWNLOAD_REDIRECTS = 10
    # MAX_DOWNLOAD_SIZE = 20 * (1024 ** 2)  # bytes
    # ARCHIVE_FOLDER_BLACKLIST = {
    #     'No .git directories': r'\.git$'
    # }

    # DISCOURSE_URL = 'https://help.nextcloud.com'

    # If given a sub category will be created at this location
    # If not given a root category will be created
    # You can get the category id here at the /categories.json route, e.g.
    # https://help.nextcloud.com/categories.json
    # DISCOURSE_PARENT_CATEGORY_ID = 26
