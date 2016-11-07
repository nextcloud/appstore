Installation
============
.. note:: This guide will use Ubuntu 16.04, Apache and PostgreSQL to set up the app store. You can of course also use different distributions and webservers, however we will not be able to support you.

There are two ways to install the store, both are mutually exclusive (means: don't mix and match):

* :ref:`development-install`: Choose this section if you want to set it up locally for development
* :ref:`production-install`: Check this section for setting up the app store on your server

.. _development-install:

Development Installation
------------------------
Certain libraries and Python packages are required before setting up your development instance::

    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git gettext libssl-dev libffi-dev

Afterwards clone the repository using git and change into it::

    git clone https://github.com/nextcloud/appstore.git
    cd appstore

The project root contains a **Makefile** which allows you to quickly set everything up by running::

    make dev-setup

.. note:: Only use this command for a local setup since it is not secure and slow!

This will automatically set up the web app using **venv**, **SQLite** as database and create a default **development** settings file in **nextcloudappstore/settings/development.py**. You need to review the development settings and change them according to your setup. An admin user with name **admin** and password **admin** will also be created.

The server can be started after activating the virtual environment first::

    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development
    python manage.py runserver

The website is available at `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_. Code changes will auto reload the server so happy developing!

Every time you start a new terminal session you will need to reactive the virtual environment and set the development settings::

    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development

We therefore recommend creating a small bash alias in your **~/.bashrc**::

    alias cda='cd path/to/appstore && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development'

.. _production-install:

Production Installation
-----------------------
Certain libraries and Python packages are required before setting up your development instance::

    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git gettext libssl-dev libffi-dev


Database Setup
~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~
Before you begin to set up the App Store, make sure that your locales are set up correctly. You can fix your locales by running::

    export LC_ALL="en_US.UTF-8"
    export LC_CTYPE="en_US.UTF-8"
    sudo dpkg-reconfigure locales

Afterwards change into your preferred target folder, clone the repository using git and change into it::

    cd /path/to/co
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next install the required libraries::

    pip install --upgrade wheel
    pip install --upgrade pip
    pip install -r requirements/base.txt
    pip install -r requirements/production.txt

Adjusting Default Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~
To get your instance running in production you need to create your production settings file in **nextcloudappstore/settings/production.py** which overwrites and enhances the settings defined in **nextcloudappstore/settings/base.py**. The production settings file is excluded from version control and should contain at least something like the following:

.. code-block:: python

    from nextcloudappstore.settings.base import *

    DEBUG = False
    USE_SSL = True

    # generate the SECRET_KEY by yourself for instance by using the following command:
    # env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo
    SECRET_KEY = 'change this!'

    ALLOWED_HOSTS = ['production-domain.com']

    DEFAULT_FROM_EMAIL = 'admin@yourdomain.com'
    ADMINS = [('Your Name', 'your-mail@example.com')]

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

    if USE_SSL:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
        CSP_IMG_SRC = ('https:',)

    # Url for serving assets like CSS, JavaScript and images
    STATIC_URL = '/static/'
    STATIC_ROOT = '/var/www/production-domain.com/static/'

    # Url for serving assets uploaded by users, ideally different domain
    MEDIA_URL = 'https://separate-domain.com/'
    MEDIA_ROOT = '/var/www/production-domain.com/media/'

    # Public and private keys for Googles recaptcha
    RECAPTCHA_PUBLIC_KEY = '<YOUR PUBLIC KEY>'
    RECAPTCHA_PRIVATE_KEY = '<YOUR PRIVATE KEY>'

    # https://docs.djangoproject.com/en/1.9/ref/settings/#std:setting-EMAIL_HOST
    EMAIL_HOST = 'localhost'

    # how many times a user is allowed to call the app upload route per day
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_upload'] = '50/day'
    # how many times a user is allowed to call the app register route per day
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_register'] = '50/day'

    # Only set this parameter if you want to use a different tmp directory for app downloads
    # RELEASE_DOWNLOAD_ROOT = '/other/tmp'

    # Only set if you want a different log location than the one in the main directory
    # LOG_FILE = '/path/to/appstore.log'

    LOG_LEVEL = 'ERROR'

    LOGGING['handlers']['file']['filename'] = LOG_FILE
    LOGGING['handlers']['file']['level'] = LOG_LEVEL
    LOGGING['loggers']['django']['level'] = LOG_LEVEL

    DISCOURSE_USER = 'tom'
    DISCOURSE_TOKEN = 'a token'

    # Overwritable defaults:

    # minimum number of comments to calculate a rating
    # RATING_THRESHOLD = 5

    # number of days to include from today in the recent ratings calculation
    # RATING_RECENT_DAY_RANGE = 90

    # VALIDATE_CERTIFICATES = True
    # CERTIFICATE_DIGEST = 'sha512'

    # MAX_DOWNLOAD_INFO_XML_SIZE = 512 * 1024  # bytes
    # MAX_DOWNLOAD_TIMEOUT = 60  # seconds
    # MAX_DOWNLOAD_REDIRECTS = 10
    # MAX_DOWNLOAD_SIZE = 20 * (1024 ** 2)  # bytes

    # certificate location configuration
    # NEXTCLOUD_CERTIFICATE_LOCATION = join(
    #    BASE_DIR, 'nextcloudappstore/core/certificate/nextcloud.crt')
    # NEXTCLOUD_CRL_LOCATION = join(
    #    BASE_DIR, 'nextcloudappstore/core/certificate/nextcloud.crl')

    # DISCOURSE_URL = 'https://help.nextcloud.com'

    # If given a sub category will be created at this location
    # If not given a root category will be created
    # You can get the category id here at the /categories.json route, e.g.
    # https://help.nextcloud.com/categories.json
    # DISCOURSE_PARENT_CATEGORY_ID = 26

    # Additional variables that are used for generating apps
    #APP_SCAFFOLDING_PROFILES = {
    #    10: {
    #        'owncloud_version': '9.1'
    #    },
    #    11: {
    #        'owncloud_version': '9.2'
    #    }
    #}


Then set the file as the active settings file::

    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production

.. note:: Absolutely make sure to generate a new **SECRET_KEY** value! Use the following command for instance to generate a token:

::

    env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo

For more settings, check the `settings documentation <https://docs.djangoproject.com/en/1.9/ref/settings/>`_.


Creating the Database Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After all settings are adjusted, create the database schema by running the following command::

    python manage.py migrate

Creating an Admin User
~~~~~~~~~~~~~~~~~~~~~~
To create the initial admin user and verify his email, run the following command::

    python manage.py createsuperuser --username admin --email admin@admin.com
    echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | python manage.py shell --settings nextcloudappstore.settings.production

The first command will ask for the password.

Loading Initial Data
~~~~~~~~~~~~~~~~~~~~
To prepopulate the database with categories and other data run the following command::

    python manage.py loaddata nextcloudappstore/**/fixtures/*.json

Initializing Translations
~~~~~~~~~~~~~~~~~~~~~~~~~
To import all translations run::

    python manage.py compilemessages
    python manage.py importdbtranslations

Placing Static Content
~~~~~~~~~~~~~~~~~~~~~~
Django web apps usually ship static content such as JavaScript, CSS and images inside the project folder's apps. In order for them to be served by your web server they need to be gathered and placed inside a folder accessible by your server. To do that first create the appropriate folders::

    sudo mkdir -p /var/www/production-domain.com/static/
    sudo mkdir -p  /var/www/production-domain.com/media/

Then copy the files into the folders by executing the following commands::

    sudo chown -R $(whoami):users /var/www
    python manage.py collectstatic
    sudo chown -R www-data:www-data /var/www

This will place the contents inside the folder configured under the key **STATIC_ROOT** and **MEDIA_ROOT** inside your **nextcloudappstore/settings/production.py**

Configuring the Web-Server
~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    Alias /schema/apps/info.xsd /path/to/appstore/nextcloudappstore/core/api/v1/release/info.xsd

    <Directory /path/to/appstore/nextcloudappstore>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    <Directory /path/to/appstore/nextcloudappstore/core/api/v1/release>
        <Files info.xsd>
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
~~~~~~~

Depending on where you have configured the log file location, you need to give your web server access to it. By default the logfile is in the main directory which also contains the **manage.py** and **README.rst**.

First create the log file::

    touch appstore.log

**Apache**:

Then give your web server access to it::

    sudo chown www-data:www-data appstore.log

Afterwards restart your web server::

    sudo systemctl restart apache2

Configure Social Logins
~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~

To fetch the latest changes from the repository change into the directory that you've cloned and run::

    git pull --rebase origin master

If not active, activate the virtual environment::

    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production

Then adjust the database schema (if changed) by running the migrations::

    python manage.py migrate

load new fixtures::

    python manage.py loaddata nextcloudappstore/**/fixtures/*.json

and install any dependencies (if changed)::

    pip install --upgrade wheel
    pip install --upgrade pip
    pip install --upgrade -r requirements/base.txt
    pip install --upgrade -r requirements/production.txt

update translations::

    python manage.py compilemessages
    python manage.py importdbtranslations

Finally run the **collectstatic** command to copy updated assets into the web server's folder::

    sudo chown -R $(whoami):users /var/www
    python manage.py collectstatic
    sudo chown -R www-data:www-data /var/www

and reload apache::

    sudo systemctl reload apache2

.. note:: If you are running Ubuntu and Apache, there is a maintenance script available by running

.. code-block:: bash

    git pull --rebase origin master
    sudo chown -R $(whoami):users /var/www
    bash scripts/maintenance/update.sh apache
    sudo chown -R www-data:www-data /var/www
