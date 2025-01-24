Nextcloud's App Store documentation
===================================

Nextcloud's App Store is an Open Source implementation for hosting Nextcloud apps and
their release information with a high focus on developer convenience, stability and
usability.

The basic ideas that form the foundation of the store include:

* Be free and open: The App Store is available under the AGPL-3.0-or-later license which offers strong copyleft so developers can profit from changes made in other versions

* Be easy to use: The App Store should be easy to use and be built in a way that users can quickly discover the most loved apps. Registration should be as easy as possible and connect users and developers by using e.g. GitHub or BitBucket logins

* Be DRY (Do not Repeat Yourself): App information should be parsed from the release archive rather than requiring developers to re-enter all the information over and over again

* Validate early: An app release should not be published without validating it beforehand. Package structure, checksums and app metadata can contain mistakes which are often discovered by users rather than developers

* Guide users: Comments sections are often used to post bug reports. This creates additional work for the developer. Therefore appropriate measures should be taken to redirect users to the correct places so issues are resolved faster and in a more convenient way

* Be hard to abuse: Rating abuse should be hard. Therefore rating systems must not be overly complex so counter measures can be taken easily

* Be well documented: APIs and developer use-cases should be documented in such a way that developers and users alike can easily discover the things they need


App Developer Documentation
---------------------------

Look here if you want to upload your own apps or use the REST API

.. toctree::
   :maxdepth: 2

   developer
   api/index

App Store Admin Documentation
-----------------------------
Look here if you want to install the store on your server and keep it up to date

.. toctree::
   :maxdepth: 2

   prodinstall
   prodinstalldocker
   configuration
   upgradenotices

App Store Developer Documentation
---------------------------------
Look here if you want to work on the app store's source code

.. toctree::
   :maxdepth: 2

   devinstall
   storedeveloper
   documentation
   translation



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
