Installation
============
.. note:: This guide will use Ubuntu 16.04, Nginx, Gunicorn and PostgreSQL to set up the app store. You can of course also use different distributions and webservers, however we will not be able to support you.

There are two ways to install the store, both are mutually exclusive (means: don't mix and match):

* :ref:`development-install`: Choose this section if you want to set it up locally for development
* :ref:`production-install`: Check this section for setting up the app store on your server

.. _development-install:

Development Installation
------------------------
Certain libraries and Python packages are required before setting up your development instance::

    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git

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

    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git


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

    pip install --upgrade wheel==0.29.0
    pip install --upgrade pip==8.1.2
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

    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        # how many times a user is allowed to call the app upload route per day
        'app_upload': '50/day'
    }

    # Only set this parameter if you want to use a different tmp directory for app downloads
    # RELEASE_DOWNLOAD_ROOT = '/other/tmp'


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

Placing Static Content
~~~~~~~~~~~~~~~~~~~~~~
Django web apps usually ship static content such as JavaScript, CSS and images inside the project folder's apps. In order for them to be served by your web server they need to be gathered and placed inside a folder accessible by your server. To do that first create the appropriate folders::

    mkdir /var/www/production-domain.com/static/
    mkdir /var/www/production-domain.com/media/

Then copy the files into the folders by executing the following command::

    python manage.py collectstatic

This will place the contents inside the folder configured under the key **STATIC_ROOT** and **MEDIA_ROOT** inside your **nextcloudappstore/settings/production.py**

Configuring the Server
~~~~~~~~~~~~~~~~~~~~~~
First install Nginx::

    sudo apt-get install nginx

Then adjust the config in **/etc/nginx/sites-enabled/default**

::

    worker_processes 1;

    events {
        worker_connections 1024;
        accept_mutex off; # set to 'on' if nginx worker_processes > 1
        use epoll;
    }

    http {
        include mime.types;
        default_type application/octet-stream;

        upstream app_server {
            server unix:/tmp/gunicorn.sock fail_timeout=0;
        }

        server {
            # if no Host match, close the connection to prevent host spoofing
            listen 80 default_server;
            return 444;
        }

        server {
            listen 80 deferred;
            gzip off;
            client_max_body_size 1G;
            server_name apps.nextcloud.com www.apps.example.com;

            root /var/www;

            location / {
                try_files $uri @proxy_to_app;
            }

            location @proxy_to_app {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto https;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_pass http://app_server;
            }

            error_page 500 502 503 504 /500.html;
            location = /500.html {
                root /var/www/html;
            }
        }
    }

.. note:: Not final

Afterwards configure SystemD to automatically start gunicorn:

**/etc/systemd/system/gunicorn.service**:

.. code-block:: ini

    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    PIDFile=/run/gunicorn/pid
    User=appstore
    Group=appstore
    Environment=PYTHONPATH=/path/to/code
    Environment=PYTHONHOME=/path/to/code/venv
    ExecStart=/path/to/code/venv/bin/gunicorn --pid /run/gunicorn/pid test:app
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target

**/etc/systemd/system/gunicorn.socket**:

.. code-block:: ini

    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn/socket
    ListenStream=0.0.0.0:9000
    ListenStream=[::]:8000

    [Install]
    WantedBy=sockets.target

**/usr/lib/tmpfiles.d/gunicorn.conf**::

    d /run/gunicorn 0755 appstore appstore -

Finally restart Nginx and enable Gunicorn::

    systemctl enable nginx.service
    systemctl enable gunicorn.socket
    systemctl restart nginx.service
    systemctl start gunicorn.socket

.. note:: Not final

Configure Social Logins
~~~~~~~~~~~~~~~~~~~~~~~
Once the AppStore is up and running and you can login to the django admin interface, the social login needs to be configured.

The AppStore uses `django-allauth <https://django-allauth.readthedocs.io>`_ for local and social login and to get the social login to work you need to add the client ID and secret key for the two supported social login provider (GitHub and BitBucket).

Inside the admin interface click on **Sites**, then on the change link and on the following page on the domain name (example.com) to edit the site.

Change the domain name to the domain the store is using and give it a descriptive name.

Then go to `https://github.com/settings/developers <https://github.com/settings/developers>`_ to create a new Application. Once you have your client ID and secret key go back to the Django admin interface and in the section **Social Accounts** add a new **Social application**. Supply the client ID and secret key generated on GitHub and assign the social application to the store site by double clicking on the site name.

Then repeat the process for the BitBucket login. To create a client ID and secret key on BitBucket follow the `documented steps described <https://confluence.atlassian.com/bitbucket/oauth-on-bitbucket-cloud-238027431.html#OAuthonBitbucketCloud-Createaconsumer>`_

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

    pip install --upgrade wheel==0.29.0
    pip install --upgrade pip==8.1.2
    pip install --upgrade -r requirements/base.txt
    pip install --upgrade -r requirements/production.txt

Finally run the **collectstatic** command to copy updated assets into the web server's folder::

    python manage.py collectstatic

and reload apache::

    systemctl reload apache2

.. note:: If you are running Ubuntu and Apache, there is a maintenance script available by running

.. code-block:: bash

    git pull --rebase origin master
    bash scripts/maintenance/update.sh apache
