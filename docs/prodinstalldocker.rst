=================================
Store Production Install (Docker)
=================================

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

The **production.py** contains all App Store specific settings that you may want to adjust. For a basic configuration take a look at :ref:`an example production configuration <production-configuration>`

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
------------------
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

Creating an Admin User
----------------------
To create the initial admin user and verify his email, run the following command::

    sudo docker-compose exec production python manage.py createsuperuser --username admin --email admin@admin.com
    sudo docker-compose exec production python manage.py verifyemail --username admin --email admin@admin.com

The first command will ask for the password.

Configure Social Logins
-----------------------
Once the App Store is up and running social login needs to be configured. The App Store uses `django-allauth <https://django-allauth.readthedocs.io>`_ for local and social login. In order to configure these logins, most providers require you to register your app beforehand.

**GitHub**

GitHub is currently the only supported social login. In order to register the App Store, go to `your application settings page <https://github.com/settings/applications/new>`_ and enter the following details:

* **Application name**: Nextcloud App Store
* **Homepage URL**: https://apps.nextcloud.com
* **Authorization callback URL**: https://apps.nextcloud.com/github/login/callback/

Afterwards your **client id** and **client secret** are displayed. These need to be saved inside the database. To do that, either log into the admin interface, change your site's domain and add GitHub as a new social application or run the following command::

    sudo docker-compose exec python manage.py setupsocial --github-client-id "CLIENT_ID" --github-secret "SECRET" --domain apps.nextcloud.com

.. note:: The above mentioned domains need to be changed if you want to run the App Store on a different server.

.. note:: For local testing use localhost:8000 as domain name. Furthermore the confirmation mail will also be printed in your shell that was used to start the development server.


.. _prod_install_release_sync_docker:

Sync Nextcloud Releases from GitHub
-----------------------------------

The App Store needs to know about Nextcloud versions because:

* app releases are grouped by app version on the app detail page
* you can :ref:`access a REST API to get all available versions <api-all-platforms>`

Before **3.2.0** releases were imported either manually or via the a shipped JSON file. This process proved to be very tedious. In **3.2.0** a command was introduced to sync releases (git tags) directly from GitHub.

You can run the command by giving it the oldest supported Nextcloud version::

     sudo docker-compose exec python manage.py syncnextcloudreleases --oldest-supported="12.0.0"

All existing versions prior to this release will be marked as not having a release, new versions will be imported and the latest version will be marked as current version.

You can also do a test run and see what kind of versions would be imported::

     sudo docker-compose exec python manage.py syncnextcloudreleases --oldest-supported="12.0.0" --print

The GitHub API is rate limited to 60 requests per second. Depending on how far back your **oldest-supported** version goes a single command might fetch multiple pages of releases. If you want to run the command more than 10 times per hour it is recommended to `obtain and configure a GitHub OAuth2 token <https://help.github.com/articles/git-automation-with-oauth-tokens/>`_.

After obtaining the token from GitHub, add it anywhere in your settings file (**production.py**), e.g.:

.. code-block:: python

    GITHUB_API_TOKEN = '4bab6b3dfeds8857371a48855d3e87d38d4b7e65'

To automate syncing you might want to add the command as a cronjob and schedule it every hour.

.. note:: Only one sync command should be run at a time, otherwise race conditions might cause unpredictable results. To ensure this use a proper cronjob daemon that supports running only one command at a time, for instance `SystemD timers <https://wiki.archlinux.org/index.php/Systemd/Timers>`_
