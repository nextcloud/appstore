==============================================
Production Install Using Docker (Experimental)
==============================================

The App Store can be installed using `Docker <https://www.docker.com/>`_. This is still work in progress and therefore not recommended for production.

Benefits & Drawbacks
====================

Benefits:

* No need to install development libraries on your server (e.g. C compiler, Node.js)
* No need to install a specific Python version
* No need to manually run update commands. Just download a new container version and start it
* Ability to run any operating system that supports your required Docker features
* Faster deployment because Python libraries, JavaScript libraries and translations come pre-built
* Easier backups since code is completely split from production data and configuration

Drawbacks:

* Knowledge of docker-compose required to change and optimize deployment
* Docker daemon `must run as root <https://askubuntu.com/a/477554>`_
* Python bugfixes and security updates are not available through your package manager; they require a container rebuild and deployment
* More complex setup due to another layer of abstraction

Choose whatever deployment mechanism fits you best

Building the Image
==================

To build the Docker image install Docker and docker-compose on your development machine, e.g.::

    sudo apt-get install docker docker-compose

and start the daemon::

    sudo systemctl enable docker
    sudo systemctl start docker

Then clone the repository and build the image::

    git clone https://github.com/nextcloud/appstore
    cd appstore
    sudo docker-compose build production

Export your container to be able to upload it to your production server::

    sudo docker save -o nextcloudappstore.tar.gz appstore_production

.. note:: Docker Hub integration would be nice


Deploying the Image
===================

Copy your built image (nextcloudappstore.tar.gz) onto your production server.

Initial Setup
-------------
These steps are only required for your initial setup.

Install Docker and docker-compose on your production server, e.g.::

    sudo apt-get install docker docker-compose

and start the daemon::

    sudo systemctl enable docker
    sudo systemctl start docker

Then change into your target installation directory, e.g.::

    cd /srv

and create a **config/** folder which is going to hold your App Store configuration files::

    sudo mkdir config/

Create the following empty files inside the config folder:

* __init__.py
* newrelic.ini
* production.py
* uwsgi.ini

Configuring uWSGI
~~~~~~~~~~~~~~~~~
uWSGI is a multi language app server which will be used to run the App Store Python code inside the container. In addition to uWSGI you will need to configure an additional web-server. A web-server is required to:

* serve static files to the client (e.g. CSS, JavaScript, images)
* encrypt the traffic with TLS
* redirect incoming requests to uWSGI

The following config file represents a minimal `uwsgi config <http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html>`_

.. code-block:: ini

    [uwsgi]
    chdir = /srv
    wsgi-file = /srv/nextcloudappstore/wsgi.py

Depending on if you are using the uwsgi protocol or http you need to configure either::

    socket = 0.0.0.0:8000

or::

    http = 0.0.0.0:8000

You may also want to configure statistics and worker threads/processes. Consult the `documentation <http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html>`_ for more information.

Configuring New Relic
~~~~~~~~~~~~~~~~~~~~~

TBD

Configuring The App Store
~~~~~~~~~~~~~~~~~~~~~~~~~

The **production.py** contains all App Store specific settings that you may want to adjust:

.. code-block:: python

    from nextcloudappstore.settings.base import *

    # DEBUG must be false to not leak sensitive content
    DEBUG = False

    # generate the SECRET_KEY by yourself for instance by using the following command:
    # env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo
    SECRET_KEY = 'change this!'

    ALLOWED_HOSTS = ['production-domain.com']

    # E-Mail settings which are used to send mails (e.g. confirm account messages)
    # for more configuration options consult the Django documentation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-EMAIL_HOST
    DEFAULT_FROM_EMAIL = 'admin@yourdomain.com'
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

    # The following lines are HTTPS only!
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    CSP_IMG_SRC = ('https:',)

    # Public and private keys for Googles recaptcha
    RECAPTCHA_PUBLIC_KEY = 'YOUR PUBLIC KEY'
    RECAPTCHA_PRIVATE_KEY = 'YOUR PRIVATE KEY'

    LOG_LEVEL = 'ERROR'
    LOGGING['handlers']['file']['filename'] = LOG_FILE
    LOGGING['handlers']['file']['level'] = LOG_LEVEL
    LOGGING['loggers']['django']['level'] = LOG_LEVEL

    # Discourse user that is allowed to create categories. This will be used
    # to automatically create categories when registering apps
    DISCOURSE_USER = 'tom'
    DISCOURSE_TOKEN = 'a token'

    #########################
    # Overridable Defaults: #
    #########################

    # Url for serving non user uploaded files like CSS, JavaScript and images
    # STATIC_URL = '/static/'

    # how many times a user is allowed to call the app upload route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_upload'] = '100/day'
    # how many times a user is allowed to call the app register route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_register'] = '100/day'

    # Only set this parameter if you want to use a different tmp directory for app downloads
    # RELEASE_DOWNLOAD_ROOT = '/other/tmp'

    # Only set if you want a different log location than the one in the main directory
    # LOG_FILE = '/path/to/appstore/appstore.log'

    # minimum number of comments to calculate a rating
    # RATING_THRESHOLD = 5

    # number of days to include from today in the recent ratings calculation
    # RATING_RECENT_DAY_RANGE = 90

    # VALIDATE_CERTIFICATES = True
    # Algorithm which is used to sign and verify app releases. The digest is
    # persisted when saving a release so changing this parameter will only
    # affect new releases. Do not forget to update the app developer docs!
    # CERTIFICATE_DIGEST = 'sha512'

    # MAX_DOWNLOAD_FILE_SIZE = 1024 ** 2  # bytes
    # MAX_DOWNLOAD_TIMEOUT = 60  # seconds
    # MAX_DOWNLOAD_REDIRECTS = 10
    # MAX_DOWNLOAD_SIZE = 20 * (1024 ** 2)  # bytes
    # ARCHIVE_FOLDER_BLACKLIST = {
    #     'No .git directories': r'\.git$'
    # }

    # certificate location configuration
    # NEXTCLOUD_CERTIFICATE_LOCATION = join(
    #    BASE_DIR, 'nextcloudappstore/certificate/nextcloud.crt')
    # NEXTCLOUD_CRL_LOCATION = join(
    #    BASE_DIR, 'nextcloudappstore/certificate/nextcloud.crl')

    # DISCOURSE_URL = 'https://help.nextcloud.com'

    # If given a sub category will be created at this location
    # If not given a root category will be created
    # You can get the category id here at the /categories.json route, e.g.
    # https://help.nextcloud.com/categories.json
    # DISCOURSE_PARENT_CATEGORY_ID = 26

    # Additional variables that are used for generating apps
    # APP_SCAFFOLDING_PROFILES = {
    #     11: {
    #         'owncloud_version': '9.2'
    #     }
    # }



Configuring Your Database
~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Configuring Your Web-Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Starting the Image
------------------

To start the image grab a copy of our `docker-compose.yml <https://github.com/nextcloud/appstore/blob/master/docker-compose.yml>`_ or create your own. Place the file in your designated directory and run it::

    cd /srv
    wget https://github.com/nextcloud/appstore/blob/master/docker-compose.yml
    docker-compose up production


then load your image and run it::

    sudo docker load -i /path/to/nextcloudappstore.tar.gz
    sudo docker-compose up production

The following directories will be created initially:

* static: holds read only files which need to be served by your web-server
* media: holds user uploaded files


.. note:: You can create whatever setup you like to by changing your **production.py** and **docker-compose.yml**.

The **static** directory will be populated with static files when a container is started and all database migrations and fixtures will be imported.
