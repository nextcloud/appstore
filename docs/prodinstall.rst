Store Production Installation
=============================

There are two ways to install the store, both are mutually exclusive (means: don't mix and match). If you are looking for a development setup, proceed to :doc:`devinstall`, otherwise continue.

.. note:: This guide will use Ubuntu 22.04, Apache and PostgreSQL to set up the app store. You can of course also use different distributions and web-servers, however we will not be able to support you.

Installing Packages
-------------------
First you want to switch your machine to an up to date Node.js (16) and NPM (8) versions::

    cd ~
    curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -
    sudo apt -y install nodejs -y


Then install the following libraries::

    sudo apt-get update
    sudo apt-get install python3-venv python3-pip python3-wheel build-essential git libpq-dev gettext


Database Setup
--------------
Then install the database::

    sudo apt-get install postgresql

configure it::

    echo "listen_address = '127.0.0.1'" | sudo tee -a /etc/postgresql/14/main/pg_ident.conf
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
    pip install poetry==1.4.2
    poetry install

Adjusting Default Settings
--------------------------
To get your instance running in production you need to create your production settings file in **nextcloudappstore/settings/production.py** which overwrites and enhances the settings defined in **nextcloudappstore/settings/base.py**. The production settings file is excluded from version control. For a basic configuration take a look at :ref:`an example production configuration <production-configuration>`

Then set the file as the active settings file::

    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production


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

    python manage.py loaddata nextcloudappstore/core/fixtures/*.json

Initializing Translations
-------------------------
To import all translations run::

    python manage.py compilemessages
    python manage.py importdbtranslations

Building the Frontend
---------------------

To build the frontend run::

    npm ci
    npm run build

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

    WSGIDaemonProcess apps python-home=/path/to/appstore/.venv python-path=/path/to/appstore
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
            Header always set X-Content-Type-Options nosniff
            Header always set X-XSS-Protection: 1; mode=block
        </Files>
        <Files database.xsd>
            Require all granted
            Header always set X-Content-Type-Options nosniff
            Header always set X-XSS-Protection: 1; mode=block
        </Files>
    </Directory>

    <Directory /var/www/production-domain.com/static/>
        Require all granted
        AllowOverride None
        Header always set X-Content-Type-Options nosniff
        Header always set X-XSS-Protection: 1; mode=block
    </Directory>

    <Directory /var/www/production-domain.com/media/>
        Require all granted
        AllowOverride None
        Header always set X-Content-Type-Options nosniff
        Header always set X-XSS-Protection: 1; mode=block
    </Directory>

    </VirtualHost>

.. note:: Your configuration will look different depending on where you place your static files and if you enable SSL. This is just a very minimal non HTTPS example.

.. note:: It could be that you need to enable **mod_headers**. To do this simply run **sudo a2enmod headers**

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


.. _prod_install_release_sync:

Sync Nextcloud Releases from GitHub
-----------------------------------

The App Store needs to know about Nextcloud versions because:

* app releases are grouped by app version on the app detail page
* you can :ref:`access a REST API to get all available versions <api-all-platforms>`

Before **3.2.0** releases were imported either manually or via the a shipped JSON file. This process proved to be very tedious. In **3.2.0** a command was introduced to sync releases (git tags) directly from GitHub.

The GitHub API now requires you to be authenticated so you need to `obtain and configure a GitHub OAuth2 token <https://help.github.com/articles/git-automation-with-oauth-tokens/>`_ before you run the sync command.

After obtaining the token from GitHub, add it anywhere in your settings file (**nextcloudappstore/settings/production.py**), e.g.:

.. code-block:: python

    GITHUB_API_TOKEN = '4bab6b3dfeds8857371a48855dse87d38d4b7e65'

You can run the command by giving it the oldest supported Nextcloud version::

     python manage.py syncnextcloudreleases --oldest-supported="12.0.0"

All existing versions prior to this release will be marked as not having a release, new versions will be imported and the latest version will be marked as current version.

You can also do a test run and see what kind of versions would be imported::

     python manage.py syncnextcloudreleases --oldest-supported="12.0.0" --print

To automate syncing you might want to add the command as a cronjob and schedule it every hour.

.. note:: Only one sync command should be run at a time, otherwise race conditions might cause unpredictable results. To ensure this use a proper cronjob daemon that supports running only one command at a time, for instance `SystemD timers <https://wiki.archlinux.org/index.php/Systemd/Timers>`_

.. note:: If run the command outside of your virtual environment you need to prefix the full path to the desired Python executable, e.g.

::

    poetry run ./manage.py syncnextcloudreleases --oldest-supported="12.0.0"

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
