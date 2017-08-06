Production Installation
=======================

There are two ways to install the store, both are mutually exclusive (means: don't mix and match). If you are looking for a development setup, proceed to :doc:`devinstall`, otherwise continue.

.. note:: This guide will use Ubuntu 16.04, Apache and PostgreSQL to set up the app store. You can of course also use different distributions and web-servers, however we will not be able to support you.

Installing Packages
-------------------
First you want to switch your machine to an up to date Node.js version and install Yarn::

    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -
    echo "deb https://deb.nodesource.com/node_8.x xenial main" | sudo tee /etc/apt/sources.list.d/nodesource.list
    echo "deb-src https://deb.nodesource.com/node_8.x xenial main" | sudo tee -a /etc/apt/sources.list.d/nodesource.list

    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

Then install the following libraries::

    sudo apt-get update
    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git gettext libssl-dev libffi-dev nodejs yarn


Database Setup
--------------
Then install the database::

    sudo apt-get install postgresql

configure it::

    echo "listen_address = '127.0.0.1'" | sudo tee -a /etc/postgresql/9.5/main/pg_ident.conf
    sudo systemctl restart postgresql.service

and create a user and database::

    sudo -s
    su - postgres
    psql
    CREATE USER nextcloudappstore WITH PASSWORD 'password';
    CREATE DATABASE nextcloudappstore OWNER nextcloudappstore;
    \q
    exit
    exit

.. note:: Use your own password instead of the password example!

App Store Setup
---------------
Before you begin to set up the App Store, make sure that your locales are set up correctly. You can fix your locales by running::

    export LC_ALL="en_US.UTF-8"
    export LC_CTYPE="en_US.UTF-8"
    sudo dpkg-reconfigure locales

Afterwards change into your preferred target folder, clone the repository using git and change into it::

    cd /path/to/target
    git clone https://github.com/nextcloud/appstore.git
    cd appstore

Afterwards set up a new virtual environment by running the following command::

    python3 -m venv venv

This will create a local virtual environment in the **venv** folder. You only need to do this once in the beginning.

Then activate it::

    source venv/bin/activate

.. note:: The above command changes your shell settings for the current session only, so once you launch a new terminal you need to run the command again to register all the paths.

.. note:: Keep in mind that you need to have the virtual environment activated for all the following commands

Installing Required Libraries
-----------------------------

Next install the required libraries::

    pip install --upgrade wheel
    pip install --upgrade pip
    pip install -r requirements/base.txt
    pip install -r requirements/production.txt

Adjusting Default Settings
--------------------------
To get your instance running in production you need to create your production settings file in **nextcloudappstore/settings/production.py** which overwrites and enhances the settings defined in **nextcloudappstore/settings/base.py**. The production settings file is excluded from version control and should contain at least something like the following:

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

    # Path to where your static content lies (e.g. CSS, JavaScript and images)
    # This should point to a directory served by your web-server
    STATIC_ROOT = '/var/www/production-domain.com/static/'

    # Url for serving content uploaded by users, ideally different domain
    MEDIA_URL = 'https://separate-domain.com/'

    # Path to where user uploaded content lies, should point to a directory
    # served by your web-server
    MEDIA_ROOT = '/var/www/production-domain.com/media/'

    # Public and private keys for Googles recaptcha
    RECAPTCHA_PUBLIC_KEY = '<YOUR PUBLIC KEY>'
    RECAPTCHA_PRIVATE_KEY = '<YOUR PRIVATE KEY>'

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
    # LOG_FILE = '/path/to/appstore.log'

    # minimum number of comments to calculate a rating
    # RATING_THRESHOLD = 5

    # number of days to include from today in the recent ratings calculation
    # RATING_RECENT_DAY_RANGE = 90

    # VALIDATE_CERTIFICATES = True
    # CERTIFICATE_DIGEST = 'sha512'

    # MAX_DOWNLOAD_FILE_SIZE = 1024 * 1024  # bytes
    # MAX_DOWNLOAD_TIMEOUT = 60  # seconds
    # MAX_DOWNLOAD_REDIRECTS = 10
    # MAX_DOWNLOAD_SIZE = 20 * (1024 ** 2)  # bytes

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


Then set the file as the active settings file::

    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production

.. note:: Absolutely make sure to generate a new **SECRET_KEY** value! Use the following command for instance to generate a token:

::

    env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo

For more settings, check the `settings documentation <https://docs.djangoproject.com/en/1.9/ref/settings/>`_.


Creating the Database Schema
----------------------------
After all settings are adjusted, create the database schema by running the following command::

    python manage.py migrate

Creating an Admin User
----------------------
To create the initial admin user and verify his email, run the following command::

    python manage.py createsuperuser --username admin --email admin@admin.com
    python manage.py verifyemail --username admin --email admin@admin.com

The first command will ask for the password.

Loading Initial Data
--------------------
To pre-populate the database with categories and other data run the following command::

    python manage.py loaddata nextcloudappstore/**/fixtures/*.json

Initializing Translations
-------------------------
To import all translations run::

    python manage.py compilemessages
    python manage.py importdbtranslations

Building the Frontend
---------------------

To build the frontend run::

    yarn install
    yarn run build

Placing Static Content
----------------------
Django web apps usually ship static content such as JavaScript, CSS and images inside the project folder's apps. In order for them to be served by your web server they need to be gathered and placed inside a folder accessible by your server. To do that first create the appropriate folders::

    sudo mkdir -p /var/www/production-domain.com/static/
    sudo mkdir -p  /var/www/production-domain.com/media/

Then copy the files into the folders by executing the following commands::

    sudo chown -R $(whoami):users /var/www
    python manage.py collectstatic
    sudo chown -R www-data:www-data /var/www

This will place the contents inside the folder configured under the key **STATIC_ROOT** and **MEDIA_ROOT** inside your **nextcloudappstore/settings/production.py**

Configuring the Web-Server
--------------------------
First install Apache and mod_wsgi::

    sudo apt-get install apache2 libapache2-mod-wsgi-py3

Then adjust the config in **/etc/apache2/sites-enabled/default.conf** and add the following configuration to your **VirtualHost** section:

.. code-block:: apache

    <VirtualHost *:80>

    WSGIDaemonProcess apps python-home=/path/to/appstore/venv python-path=/path/to/appstore
    WSGIProcessGroup apps
    WSGIScriptAlias / /path/to/appstore/nextcloudappstore/wsgi.py
    WSGIPassAuthorization On
    Alias /static/ /var/www/production-domain.com/static/
    Alias /schema/apps/info.xsd /path/to/appstore/nextcloudappstore/api/v1/release/info.xsd
    Alias /schema/apps/database.xsd /path/to/appstore/nextcloudappstore/api/v1/release/database.xsd

    <Directory /path/to/appstore/nextcloudappstore>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    <Directory /path/to/appstore/nextcloudappstore/api/v1/release>
        <Files info.xsd>
            Require all granted
        </Files>
        <Files database.xsd>
            Require all granted
        </Files>
    </Directory>

    <Directory /var/www/production-domain.com/static/>
        Require all granted
        AllowOverride None
    </Directory>

    <Directory /var/www/production-domain.com/media/>
        Require all granted
        AllowOverride None
    </Directory>

    </VirtualHost>

.. note:: Your configuration will look different depending on where you place your static files and if you enable SSL. This is just a very minimal non HTTPS example.

Finally restart Apache::

    sudo systemctl restart apache2

Logging
-------

Depending on where you have configured the log file location, you need to give your web server access to it. By default the logfile is in the main directory which also contains the **manage.py** and **README.rst**.

First create the log file::

    touch appstore.log

**Apache**:

Then give your web server access to it::

    sudo chown www-data:www-data appstore.log

Afterwards restart your web server::

    sudo systemctl restart apache2

Configure Social Logins
-----------------------
Once the App Store is up and running social login needs to be configured. The App Store uses `django-allauth <https://django-allauth.readthedocs.io>`_ for local and social login. In order to configure these logins, most providers require you to register your app beforehand.

**GitHub**

GitHub is currently the only supported social login. In order to register the App Store, go to `your application settings page <https://github.com/settings/applications/new>`_ and enter the following details:

* **Application name**: Nextcloud App Store
* **Homepage URL**: https://apps.nextcloud.com
* **Authorization callback URL**: https://apps.nextcloud.com/github/login/callback/

Afterwards your **client id** and **client secret** are displayed. These need to be saved inside the database. To do that, either log into the admin interface, change your site's domain and add GitHub as a new social application or run the following command::

    python manage.py setupsocial --github-client-id "CLIENT_ID" --github-secret "SECRET" --domain apps.nextcloud.com

.. note:: The above mentioned domains need to be changed if you want to run the App Store on a different server.

.. note:: For local testing use localhost:8000 as domain name. Furthermore the confirmation mail will also be printed in your shell that was used to start the development server.

Keeping Up To Date
------------------
Updating an instance is scripted in **scripts/maintenance/update.sh**. Depending on your distribution you will have to adjust the scripts contents.

For Ubuntu you can run the provided script::

    git pull --rebase origin master
    sudo chown -R $(whoami):users /var/www
    bash scripts/maintenance/update.sh apache
    sudo chown -R www-data:www-data /var/www

.. note:: The above commands assume that your static content is located in **/var/www**

Monitoring
----------
By default monitoring the application via New Relic is supported by simply placing a file called **newrelic.ini** into the base folder (the folder that also contains the **manage.py** file).
