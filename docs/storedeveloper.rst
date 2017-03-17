.. _development-install:

Development Installation
------------------------
First you want to switch your machine to an up to date Node.js version::

    su -c "echo 'deb https://deb.nodesource.com/node_7.x xenial main' > /etc/apt/sources.list.d/nodesource.list"
    su -c "echo 'deb-src https://deb.nodesource.com/node_7.x xenial main' > /etc/apt/sources.list.d/nodesource.list"

Certain libraries and Python packages are required before setting up your development instance::

    sudo apt-get update
    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git gettext libssl-dev libffi-dev nodejs


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
