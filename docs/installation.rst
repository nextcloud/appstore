Installation
============

The store runs on **Python 3.4 or later** and requires only **venv** to be set up.

You can check your Python version by running::

    python3 --version

**venv** is sometimes bundled with your Python 3 package (e.g. Arch Linux), however certain distributions move it into a separate package. You can find out if it is installed by running::

    python3 -m venv -h

If you get a **No module named venv** error, you need to install it first:

* **Ubuntu and Debian**::

    sudo apt-get install python3-venv


There are two ways to install the store, both are mutually exclusive (means: don't mix and match):

* :ref:`development-install`: Choose this section if you want to set it up locally for development
* :ref:`production-install`: Check this section for setting up the app store on your server


.. _development-install:

Development Installation
------------------------
First clone the repository using git and change into it::

    git clone https://github.com/nextcloud/appstore.git
    cd appstore

The project root contains a **Makefile** which allows you to quickly set everything up by running::

    make dev-setup

.. note:: Only use this command for a local setup since it is not secure and slow!

This will automatically set up the web app using **venv** and **SQLite** as database. An admin user with name **admin** and password **admin** will also be created.

The server can be started after activating the virtual environment first:

    source venv/bin/activate
    python manage.py runserver

The website is available at `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_. Code changes will auto reload the server so happy developing!


.. _production-install:

Production Installation
-----------------------
First clone the repository using git and change into it::

    git clone https://github.com/nextcloud/appstore.git
    cd appstore

Afterwards set up a new virtual environment by running the following command::

    pyvenv venv

This will create a local virtual environment in the **venv** folder. You only need to do this once in the beginning.

Then activate it::

    source venv/bin/activate

.. note:: The above command changes your shell settings for the current session only, so once you launch a new terminal you need to run the command again to register all the paths.

.. note:: Keep in mind that you need to have the virtual environment activated for all the following commands

Installing Required Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next install the required libraries::

    pip install -r requirements/base.txt

Adjusting Default Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~
To get your instance running in production you need to create your local settings file in **nextcloudappstore/local\_settings.py** which overwrites and enhances the settings defined in **nextcloudappstore/settings.py**. The local settings file is excluded from version control and should contain at least something like the following:

.. code-block:: python

    DEBUG = False

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
            'NAME': 'mydatabase',
            'USER': 'mydatabaseuser',
            'PASSWORD': 'mypassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    # Url for serving assets like CSS, JavaScript and images
    STATIC_URL = '/static/'
    STATIC_ROOT = '/var/www/production-domain.com/static/'

    # Url for serving assets uploaded by users, ideally different domain
    MEDIA_URL = 'https://separate-domain.com'
    MEDIA_ROOT = '/var/www/production-domain.com/media/'

    # Public and private keys for Googles recaptcha
    RECAPTCHA_PUBLIC_KEY = '<YOUR PUBLIC KEY>'
    RECAPTCHA_PRIVATE_KEY = '<YOUR PRIVATE KEY>'

    # https://docs.djangoproject.com/en/1.9/ref/settings/#std:setting-EMAIL_HOST
    EMAIL_HOST = 'localhost'

    # how many times a user is allowed to call the app upload route per day
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
       'app_upload_or_delete': '20/day'
    }


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
To create the initial admin user, run the following command::

    python manage.py createsuperuser --username admin --email admin@admin.com

The command will ask for the password.

Loading Initial Data
~~~~~~~~~~~~~~~~~~~~
To prepopulate the database with categories and other data run the following command::

    python manage.py loaddata nextcloudappstore/**/fixtures/*.json

Placing Static Content
~~~~~~~~~~~~~~~~~~~~~~
Django web apps usually ship static content such as JavaScript, CSS and images inside the project folder's apps. In order for them to be served by your web server they need to be gathered and placed inside a folder accessible by your server. This can be done by executing the following command::

    python manage.py collectstatic

This will place the contents inside the folder configured under the key **STATIC_ROOT** inside your **nextcloudappstore/local_settings.py**

Configuring the Server
~~~~~~~~~~~~~~~~~~~~~~
This section will explain how to set up the application using apache and mod_wsgi. If you want to use a different web server or need further information check out `the deployment documentation <https://docs.djangoproject.com/en/1.9/howto/deployment/>`_

First install apache and mod_wsgi:

* **Ubuntu and Debian**::

     sudo apt-get install apache2 libapache2-mod-wsgi

Then place the following content in the appropriate apache configuration:

.. code-block:: apacheconf

    WSGIScriptAlias / /path/to/code/nextcloudappstore/wsgi.py
    WSGIDaemonProcess production-domain.com python-path=/path/to/production-domain.com:/path/to/code/venv/lib/python3.4/site-packages/
    WSGIProcessGroup production-domain.com

    Alias /static/ /var/www/production-domain.com/static/
    Alias /robots.txt /var/www/production-domain.com/static/robots.txt
    Alias /favicon.ico /var/www/production-domain.com/static/favicon.ico

    <Directory /path/to/code/nextcloudappstore>
    <Files wsgi.py>
    Require all granted
    </Files>
    </Directory>

    <Directory /var/www/production-domain.com/static>
    Require all granted
    </Directory>

    <Directory /var/www/production-domain.com/media>
    Require all granted
    </Directory>

.. note:: **/path/to/code/venv/lib/python3.4/site-packages/** must be adjusted if you are using a newer version than Python 3.4

Finally restart apache to reload the settings::

    systemctl restart apache2.service

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

Then adjust the database schema (if changed) by running the migrations::

    python3 manage.py migrate

and install any dependencies (if changed)::

    pip install --upgrade -r requirements/base.txt

Finally run the **collectstatic** command to copy updated assets into the web server's folder:

    python manage.py collectstatic
