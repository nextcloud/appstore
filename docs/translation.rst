Translation
===========

The App Store uses Django's translation system.

Generating Translations
-----------------------

To initially add a language for translation run::

    python manage.py makemessages -l $CODE -i venv

where **$CODE** is **de** for instance. This will create the required directories and files in the **locales/** folder.

The above command only needs to be run if you want to add a new language. To update existing translation files run::

    python manage.py makemessages -a

.. note:: The above requirements require exported environment variables and installed libraries. To find out how to do that see :ref:`development-install`.


Finally each time the **.po** files are changed, they need to be compiled into a specific binary format for **gettext** using::

    python manage.py compilemessages

Further details can be looked up in `Django's documentation online <https://docs.djangoproject.com/en/1.10/topics/i18n/translation/>`_

Managing Translations
---------------------

Translations are managed on `Transifex <https://www.transifex.com/nextcloud/nextcloud/>`_. If you want to help translating the App Store, click the **Join team** button and `create an issue on our issue tracker <https://github.com/nextcloud/appstore/issues/new>`_ if your request takes longer than 2 days to process.
