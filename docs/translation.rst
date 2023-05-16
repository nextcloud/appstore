Store Translation
=================

The App Store uses Django's translation system.

Generating Translations
-----------------------

To initially add a language for translation run::

    python manage.py makemessages -l $CODE -i venv

where **$CODE** is **de** for instance. This will create the required directories and files in the **locales/** folder.

The above command only needs to be run if you want to add a new language. To update existing translation files run::

    python manage.py makemessages -a -i venv

.. note:: The above requirements require exported environment variables and installed libraries. To find out how to do that see :doc:`devinstall`.

Generating Database Translations
--------------------------------
Certain translated strings like categories are stored in the database. If you change them in the database, you need to extract them into **.po** files. To do that run::

    python manage.py create createdbtranslations
    python manage.py makemessages -a -i venv

To import the translated messages back into the database run::

    python manage.py compilemessages
    python manage.py importdbtranslations

Deploying Translations
----------------------

Each time the **.po** files are changed, they need to be compiled into a specific binary format for **gettext** using::

    python manage.py compilemessages

Further details can be looked up in `Django's documentation online <https://docs.djangoproject.com/en/1.10/topics/i18n/translation/>`_

Afterwards you want to import all the translated content in the database:

    python manage.py importdbtranslations

Managing Translations
---------------------

Translations are managed on `Transifex <https://www.transifex.com/nextcloud/nextcloud/dashboard/>`_. If you want to help translating the App Store, click the **Join team** button and `create an issue on our issue tracker <https://github.com/nextcloud/appstore/issues/new>`_ if your request takes longer than 2 days to process.

All translatable languages for the App Store can be found on its `resources page <https://www.transifex.com/nextcloud/nextcloud/appstore/>`_. Select the language you want to translate and hit the **Translate** or **view strings online** button.

Translated content will be pulled daily from Transifex.
