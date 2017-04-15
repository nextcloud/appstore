Development Installation
========================
This setup details a local development installation in order to work and test App Store changes. The App Store is build using `Django <https://www.djangoproject.com/>`_. The frontend is written in TypeScript and does not yet use a JavaScript framework; this decision might change however depending on how JavaScript intensive things might become.

.. note:: Only use this guide for your local development installation which is **not connected to the Internet** since your installation will be be initialized with insecure defaults!

Installing Packages
-------------------

First you want to switch your machine to an up to date Node.js version and install Yarn::

    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -
    echo "deb https://deb.nodesource.com/node_7.x xenial main" | sudo tee /etc/apt/sources.list.d/nodesource.list
    echo "deb-src https://deb.nodesource.com/node_7.x xenial main" | sudo tee -a /etc/apt/sources.list.d/nodesource.list

    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

Then install the following libraries::

    sudo apt-get update
    sudo apt-get install python3-venv python3-wheel libxslt-dev libxml2-dev libz-dev libpq-dev build-essential python3-dev python3-setuptools git gettext libssl-dev libffi-dev nodejs yarn


Download the Source
-------------------
Clone the repository using git and change into it::

    git clone https://github.com/nextcloud/appstore.git
    cd appstore

App Store Setup
---------------
The project root contains a **Makefile** which allows you to quickly set everything up by running::

    make dev-setup

This will automatically set up the web app using **venv**, **SQLite** as database and create a default **development** settings file in **nextcloudappstore/settings/development.py**. You need to review the development settings and change them according to your setup. An admin user with name **admin** and password **admin** will also be created.

Launching the Development Server
--------------------------------
The server can be started after activating the virtual environment first::

    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development
    python manage.py runserver

The website is available at `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_. Code changes will auto reload the server so happy developing! For more documentation on development, check out :doc:`storedeveloper`

Every time you start a new terminal session you will need to reactive the virtual environment and set the development settings::

    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development

We therefore recommend creating a small bash alias in your **~/.bashrc**::

    alias cda='cd path/to/appstore && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development'

Keeping Up to Date
------------------

.. note:: Before updating it is recommended to stop the development server.

To check out the latest changes simply pull::

    git pull --rebase origin master

then make sure that the virtual environment is enabled and install new libraries::

    make update-dev-deps

apply new database migrations::

    python manage.py migrate

and build the latest frontend::

    yarn run build


