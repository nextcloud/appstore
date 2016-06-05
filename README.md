# Nextcloud App Store

[![Build Status](https://travis-ci.org/nextcloud/appstore.svg?branch=master)](https://travis-ci.org/nextcloud/appstore)

## Dependencies

* Python >= 3.4

## Installation

To get started, change into your destination folder and clone the repository:

    git clone https://github.com/nextcloud/appstore.git

Then change into the directory:

    cd appstore

### Setting Up a Virtual Environment (Optional)

Instead of installing all Python libraries globally, it is recommended to use [pyvenv](https://docs.python.org/3/library/venv.html) to keep things locally. That way you can make sure to not interfere with other things.

The package is included in Python 3.3 or later but some distributions split out certain parts from the default distribution and require you to install them manually. On Ubuntu for instance you would need to install the following package first:

    sudo apt-get install python3-venv

Afterwards set up a new virtual environment by running the following command:

    pyvenv venv

This will create a local virtual environment in the **venv** folder. You only need to do this once in the beginning.

Then activate it:

    source venv/bin/activate

**Note**: The above command changes your shell settings for the current session only, so once you launch a new terminal you need to run the command again to register all the paths.

**Note**: Keep in mind that you need to have the virtual environment activated for all the following commands

### Install Libraries

Next install the required libraries. By default pip (the package manager) is shipped by default, however certain distributions split it out into a separate repository. On Ubuntu for instance you would need to install the following package first:

    sudo apt-get install python3-pip

If you used a virtual environment the libraries will be installed locally, otherwise pip tries to install them globally so you might need to add sudo before the next command:

    pip3 install -r requirements.txt

### Adjust Settings
To get your instance running in development or in production you need to create your local settings file in **nextcloudappstore/local_settings.py** which overwrites and enhances the settings defined in **nextcloudappstore/local_settings.py**. The local settings file is excluded from version control.

For development paste in the following file contents:
```python
DEBUG = True

# generate the SECRET_KEY by yourself for instance by using the following command:
# env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo
SECRET_KEY = 'change this!'
```

For more settings, check the [documentation](https://docs.djangoproject.com/en/1.9/ref/settings/)

**Note**: Absolutely make sure to generate a new **SECRET_KEY** value! Use the following command for instance to generate a token:

    env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64; echo

### Create Database
After all settings are adjusted, create the database schema by running the following command:

    python3 manage.py migrate

This will take all the existing database migrations, run them and adjust the database schema. If you later on change models (remove fields, change fields or add fields) you need to run the following commands:

    python3 manage.py makemigrations
    python3 manage.py migrate

The first command will create the necessary migrations, the second one will apply the existing ones.

### Create an Admin User
To create the initial admin user, run the following command:

    python manage.py createsuperuser

The commmand will ask for the necessary information.

### Start the Server
Finally start the development server using the following command:

    python3 manage.py runserver

The website is available at [http://127.0.0.1:8000](http://127.0.0.1:8000). Code changes will autoreload the server so happy developing!

**Note**: Do not use the development server in production! It is very slow and insecure.


## Deploying to Production
For production use you also need to create a **nextcloudappstore/local_settings.py** using something similar to this:

```python
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

# Url for serving assets like CSS and images
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/production-domain.com/static/'

# Url for serving stuff uploaded by users
MEDIA_URL = 'https://separate-domain.com/upload/'
MEDIA_ROOT = '/var/www/example.com/upload/'
```

For more information about web server setup, take a look at [the deployment documentation](https://docs.djangoproject.com/en/1.9/howto/deployment/)

TODO:
* check which server should be set up
* document pyvenv setup for webserver

## Keeping Up To Date
To fetch the latest changes from the repository run:

    git pull --rebase origin master

Aftewards adjust the database schema by running the migrations:

    python3 manage.py migrate

On production you will need to run the collectstatic command to copy updated assets into the target folders:

    python3 manage.py collectstatic
