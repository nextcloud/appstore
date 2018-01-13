==============================================
Production Install Using Docker (Experimental)
==============================================

The App Store can be installed using `Docker <https://www.docker.com/>`_. This is still work in progress and therefore not recommended for production.

Benefits and Drawbacks
======================
Docker is just another technology with its own upsides and downsides. Make an educated decision on whether you want to use it or go for an alternative.

**Benefits**:

* No need to install development libraries on your server (e.g. C compiler, Node.js)
* No need to install a specific Python version
* No need to manually run update commands. Just download a new container version and start it
* Ability to run any operating system that supports your required Docker features
* Faster deployment because Python libraries, JavaScript libraries and translations come pre-built
* Easier backups since code is completely split from production data and configuration

**Drawbacks**:

* Knowledge of docker-compose required to change and optimize deployment
* Docker daemon `must run as root <https://askubuntu.com/a/477554>`_
* Python bugfixes and security updates are not available through your package manager; they require a container rebuild and deployment
* Much more complex setup due to another layer of abstraction


General Information
===================

This page will detail a setup with the following configuration

* the host runs Ubuntu 16.04
* PostgreSQL and Nginx are run on the host

If you want to run a different setup you need to provide your own **docker-compose.yml** and adjust your settings accordingly.

Building the Image
==================

To build the Docker image install Git, Docker and docker-compose on your development machine, e.g.::

    sudo apt-get install docker docker-compose git

and start the daemon::

    sudo systemctl enable docker
    sudo systemctl restart docker

Then clone the repository and build the image::

    git clone https://github.com/nextcloud/appstore
    cd appstore
    git checkout tags/VERSION
    sudo docker-compose build production

Export your container to be able to upload it to your production server::

    sudo docker save -o nextcloudappstore.tar.gz appstore_production

.. note:: Docker Hub integration would be nice


Deploying the Image
===================

Upload the **nextcloudappstore.tar.gz** archive onto your production server.


Initial Setup
=============
These steps are only required for your initial setup.

Install Docker and docker-compose on your production server, e.g.::

    sudo apt-get install docker docker-compose

and start the daemon::

    sudo systemctl enable docker
    sudo systemctl restart docker

Then create and change into your target installation directory, e.g.::

    sudo mkdir -p /srv
    cd /srv

and create a **config/** folder which is going to hold your App Store configuration files::

    sudo mkdir -p config/

Next create empty files inside the config folder::

    sudo touch config/__init__.py
    sudo touch config/production.py
    sudo touch config/uwsgi.ini
    sudo touch config/newrelic.ini  # only needed if you run New Relic

Configuring uWSGI
-----------------
uWSGI is a multi language app server which will be used to run the App Store's Python code inside the container. In addition to uWSGI you will need to configure an additional web-server. A web-server is required to:

* serve static files to the client (e.g. CSS, JavaScript, images)
* encrypt the traffic with TLS
* redirect incoming requests to uWSGI

The following config file represents a minimal `uwsgi config <http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html>`_

.. code-block:: ini

    [uwsgi]
    chdir = /srv
    wsgi-file = /srv/nextcloudappstore/wsgi.py
    master = true
    processes = 10
    vacuum = true
    uid = nextcloudappstore
    gid = nextcloudappstore
    socket = 0.0.0.0:8000

If your server does not support the uWSGI protocol natively, replace **socket** with::

    http = 0.0.0.0:8000

You may also want to configure statistics and adjust threads/processes to whatever works best on your server. Consult the `documentation <http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html>`_ for more information.

Configuring The App Store
-------------------------

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
            'HOST': '172.17.0.1',
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

    LOG_FILE = join(BASE_DIR, 'logs/appstore.log')
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

    # Url or domain for serving user uploaded files
    # MEDIA_URL = '/media/'

    # how many times a user is allowed to call the app upload route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_upload'] = '100/day'
    # how many times a user is allowed to call the app register route per day
    # REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['app_register'] = '100/day'

    # Only set this parameter if you want to use a different tmp directory for app downloads
    # RELEASE_DOWNLOAD_ROOT = '/tmp'

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

Setting Up Your Database
------------------------

Install PostgreSQL on your host machine::

    sudo apt-get install postgresql

To allow the container to connect to it open **/etc/postgresql/9.5/main/postgresql.conf** and modify/add the following section::

    listen_addresses = '127.0.0.1,172.17.0.1'

Then whitelist your container IP in **/etc/postgresql/9.5/main/pg_hba.conf**::

    host    nextcloudappstore nextcloudappstore 172.17.0.2/32       md5

.. note:: This expects the database user and database to be named **nextcloudappstore**, your container IP to be **172.17.0.2** and host to run on **172.17.0.1**

Then enable and start it::

    sudo systemctl enable postgresql.service
    sudo systemctl restart postgresql.service

and create a user and database::

    sudo -s
    su - postgres
    psql
    CREATE USER nextcloudappstore WITH PASSWORD 'password';
    CREATE DATABASE nextcloudappstore OWNER nextcloudappstore;
    \q
    exit

.. note:: Use your own password instead of the password example!

Configuring Your Web-Server
---------------------------

First install nginx::

    sudo apt-get install nginx

Then create a new configuration for it in **/etc/nginx/sites-available/nextcloudappstore**:

.. code-block:: nginx

    upstream nextcloudappstore {
        server 127.0.0.1:8000;
    }

    server {
        listen 80 default_server;
        listen [::]:80 default_server;

        # Redirect all HTTP requests to HTTPS with a 301 Moved Permanently response.
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name apps.nextcloud.com;
        charset     utf-8;

        # replace this with your ssl certificates
        ssl_certificate /etc/nginx/ssl/nextcloudappstore.crt;
        ssl_certificate_key /etc/nginx/ssl/nextcloudappstore.key;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2;
        ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
        ssl_prefer_server_ciphers on;
        ssl_prefer_server_ciphers on;
        ssl_stapling on;
        ssl_stapling_verify on;
        ssl_trusted_certificate /etc/ssl/private/ca-certs.pem;

        add_header Strict-Transport-Security max-age=15768000;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        client_max_body_size 75M;
        location /media  {
            alias /srv/media;
        }

        location /static {
            alias /srv/static;
        }

        location / {
            uwsgi_pass nextcloudappstore;
            include uwsgi_params;
        }
    }

Finally replace your default configuration::

    sudo rm /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/nextcloudappstore /etc/nginx/sites-enabled/default
    sudo systemctl enable nginx
    sudo systemctl restart nginx

Configuring New Relic (Optional)
--------------------------------

TBD

Creating Docker-Compose Configuration
-------------------------------------

Either create your own configuration or grab a copy of our `docker-compose.yml <https://github.com/nextcloud/appstore/blob/master/docker-compose.yml>`_ and modify it if necessary. Place the file in your designated directory::

    cd /srv
    sudo wget https://raw.githubusercontent.com/nextcloud/appstore/master/docker-compose.yml

Starting the Image
==================
First load the latest uploaded image::

    sudo docker load -i /path/to/nextcloudappstore.tar.gz

Then change into your server directory and start the container::

    cd /srv
    sudo docker-compose up production

The following directories will be created initially:

* **static**: holds read only files which need to be served by your web-server
* **media**: holds user uploaded files
* **logs**: contains your log file

The **static** directory will be populated with static files when a container is started and all database migrations and fixtures will be imported.

