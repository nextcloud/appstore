ncdev Integration
=================

.. note:: ncdev is still work in progress, this is a specification of how it should work

`ncdev <https://github.com/nextcloud/ncdev>`_ implements the :doc:`app store REST api <restapi>` and allows you to easily manage your apps through your CLI.


Configuration
-------------

ncdev's configuration is store inside **~/.ncdevrc** and the following settings are available for the app store:

.. code-block:: ini

    [appstore]
    user = username
    password = password
    token = a132dfasljkjkdf
    url = https://apps.nextcloud.com

* **user**: Your app store user name
* **password**: Your app store password
* **token**: Your app store token if you don't want to add user and password. If all are present, user and password will be ignored.
* **url**: Url to the app store

Furthermore ncdev expects your app certificates to be present in **~/.nextcloud/certificates/APP_ID.key** and ****~/.nextcloud/certificates/APP_ID.crt** where **APP_ID** is your app's id (same as your app folder).

Using ncdev
-----------
The following commands are available:

* :ref:`ncdev-register-app`

* :ref:`ncdev-upload-release`

* :ref:`ncdev-delete-release`

* :ref:`ncdev-delete-app`

.. _ncdev-register-app:

Register a New App
~~~~~~~~~~~~~~~~~~
To register a new app use::

    ncdev appstore register APP_ID

where **APP_ID** is the app's id that you want to register.

.. note:: Certificates need to be in place

.. note:: Registering an already present app id with a new certificate will delete all its existing releases!

.. _ncdev-upload-release:

Upload a New Release
~~~~~~~~~~~~~~~~~~~~
To upload a new release use::

    ncdev appstore release https://github.com/nextcloud/news/archive/8.8.0.tar.gz

where the link is the url to your app release archive. Ncdev will first download and create the app signature, then submit the link including the signature. If the release exists already it will be overwritten. You can omit that step by explicitly providing a signature::

    ncdev appstore release https://github.com/nextcloud/news/archive/8.8.0.tar.gz --signature THE_SIGNATURE

To upload a **nightly** release use::

    ncdev appstore release https://github.com/nextcloud/news/archive/8.8.0.tar.gz --nightly


.. _ncdev-delete-app:

Delete a Release
~~~~~~~~~~~~~~~~
To delete a release use::

    ncdev appstore delete news@8.8.0

where **news** is your app's id and **8.8.0** is the app version to delete. You will be asked to confirm your decision.

.. _ncdev-delete-release:

Delete an App and All Its Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To delete an app and all its releases use::

    ncdev appstore delete news

where **news** is your app's id. You will be asked to confirm your decision.
