ncdev Integration
=================

`ncdev <https://github.com/nextcloud/ncdev>`_ implements the :doc:`app store REST api <restapi>` and allows you to easily manage your apps through your CLI.


Configuration
-------------

ncdev's configuration is store inside ~/.ncdevrc and the following settings are available for the app store:

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

Using ncdev
-----------
The following commands are available:

* :ref:`ncdev-upload-release`

* :ref:`ncdev-delete-release`

* :ref:`ncdev-delete-app`

.. _ncdev-upload-release:

Upload a New Release
~~~~~~~~~~~~~~~~~~~~
To upload a new release use::

    ncdev appstore release https://github.com/nextcloud/news/archive/8.8.0.tar.gz --checksum 65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15

where the link is the url to your app release archive. Checksum is an optional parameter and can be computed by using::

    sha256sum 8.8.0.tar.gz

If you omit the checksum it will be computed for you.

The first time you upload an app you will be registered as app owner for the app's id.

If the release exists already it will be overwritten.

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
