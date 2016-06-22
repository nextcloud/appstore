.. nextcloudappstore documentation master file, created by
   sphinx-quickstart on Sat Jun 18 23:44:17 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Nextcloud's App Store documentation
===================================

Nextcloud's App Store is an Open Source implementation for hosting app and
releases information with a high focus on developer convenience, stability and
usability.

The basic ideas that form the foundation of the store include:

* Be free and open: The App Store is available under the AGPLv3 or later which offers a strong copyleft so developers can profit from changes made in other versions

* Be easy to use: The app store should be easy to use and be built in a way that users can quickly discover the most loved apps. Registration should be as easy as possible and connect users and developers by using GitHub and BitBucket logins.

* Be DRY (Do not Repeat Yourself): App information should be parsed from the release archive rather than requiring developers to re-enter all the information over and over again

* Validate early: An app release should not be published without validating it beforehand. Package structure, checksums and app metadata can contain mistakes which are often discovered by users rather then developers

* Guide users: Comments sections are often places where bug reports are posted. This creates additional work for the developer. Therefore appropriate measures should be taken to redirect users to the correct places before so issues are resolved faster and in a more convenient way

* Be hard to abuse: Rating abuse should be hard. Therefore rating systems must not be overly complex so counter measures can be taken easily

* Be well documented: APIs and developer use-cases should be documented in such a way that developers and users alike can easily discover the things they need


App Developer Documentation
---------------------------

Look here if you want to upload your own apps or use the REST API

.. toctree::
   :maxdepth: 2

   developer
   ncdev
   restapi

App Store Developer Documentation
---------------------------------
Look here if you want to work on the app store's source code or install it on your own server

.. toctree::
   :maxdepth: 2

   installation
   documentation



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

