App Developer Guide
===================

Most of today's developers publish their source code on GitHub, BitBucket or on their own GitLab instance. These tools typically also provide a way to release new versions based on Git tags or by uploading custom archives.

Advanced users and developers typically prefer to download the app directly from these services whereas administrators or novice users look for app releases on the App Store. This means that you have to take care of publishing two releases on two different platforms.

We want to avoid duplication and make it harder to ship broken releases by mistake, therefore we went for the following solution:

* Your app's source code is hosted on GitHub or a similar service

* You should use Git tags to create new releases on these services

* Archives are typically created automatically for you. If you require compilation or other transformations like minification, you should upload a pre-built archive to the appropriate releases page

This keeps your repository up to date and satisfies the needs of developers and advanced users.

Publishing Apps on the App Store
--------------------------------
Hosting the archive on a different host means of course that we can not guarantee that the contents have not been tampered with. Neither can we guarantee that the actual app developer uploaded the app. Therefore we require you to sign your app using a certificate.

Obtaining a Certificate
~~~~~~~~~~~~~~~~~~~~~~~
The certificates should be stored in **~/.nextcloud/certificates/** so first create the folder if it does not exist yet::

    mkdir -p ~/.nextcloud/certificates/

Then change into the directory::

    cd ~/.nextcloud/certificates/

and generate your private certificate and CSR::

    openssl req -nodes -newkey rsa:4096 -keyout APP_ID.key -out APP_ID.csr -subj "/CN=APP_ID"

Replace **APP_ID** with your app id, e.g. if your app had an id called **news** you would execute the following command::

    openssl req -nodes -newkey rsa:4096 -keyout news.key -out news.csr -subj "/CN=news"

.. note:: Keep in mind that an app id must only contain lowercase ASCII characters and underscores!

Then post the contents of your **APP_ID.csr** (e.g. **~/.nextcloud/certificates/news.csr**) on `on our certificate repository <https://github.com/nextcloud/app-certificate-requests>`_ as pull request and configure your GitHub account to show your mail address in your profile.

We might ask you for further information to verify that you're the legitimate owner of the application. Make sure to keep the private key file (**APP_ID.key**, e.g. **~/.nextcloud/certificates/news.key**) secret and not disclose it to any third-parties.

After we approved your certificate, we will post your signed public certificate (APP_ID.crt) as a response in your app's directory. Take the contents and store it in the same folder with the file name **APP_ID.crt** (e.g. **~/.nextcloud/certificates/news.crt**). Make sure to get rid of excess whitespace at the beginning and end of your file. Your public signed certificate's file contents should look similar to this::

    -----BEGIN CERTIFICATE-----
    MIID+TCCAeECAhAMMA0GCSqGSIb3DQEBCwUAMG0xCzAJBgNVBAYTAlVTMQ8wDQYD
    VQQIDAZCb3N0b24xFjAUBgNVBAoMDW93bkNsb3VkIEluYy4xNTAzBgNVBAMMLG93
    bkNsb3VkIENvZGUgU2lnbmluZyBJbnRlcm1lZGlhdGUgQXV0aG9yaXR5MB4XDTE2
    MDcyNjEwMTIyOFoXDTI2MDcyNDEwMTIyOFowFzEVMBMGA1UEAwwMZm9sZGVycGxh
    eWVyMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8BnaiY7+oPMmYalU
    Cpv/U+36PUTQd3r9t73l7opUyv7F2yshrgKk9jdINOWZaPYxFi5mSnolu6KP/nNq
    Bsh7HTHFo9xmVg2lia4WxmO23GBp94GEj4irYSP3FcrrT+aLBmr3sM2zxfIWJ9K/
    9wC8rFhyQjMaQLqC48VRjz8eI6rRSAUrcY+B6GAB0O2XZifSYVgzwh3lV1Xno2uT
    69+V5HfXEEz8u5YRnoFBC8hfaRzGlnm0cUZrVEgEcCjt1pPf+HeGUnHafT8uUbET
    7Ys6QCQoaiKy7D7eiUh2kOOcChFAxiGX+9ahiIESZUrlDs8m8rmoa8C3fqho4C9g
    nwEoowIDAQABMA0GCSqGSIb3DQEBCwUAA4ICAQAZts21nfQGzkPsiDseIZjg1Dh7
    KavuEjxJHqSbTlqi1W9CxievQF205IbfuRLsbsi1Kw1hFivse//nTkFiMvgdqKsM
    zSzsUq24tjWFDpNVHgVoPCBG6t7yYP6PdWNZtPSt76w8l7fAo9Fm2tBlFvMfF4Pe
    3nveZjV5ns71oFpxLJobl25xj4Q63DKRoN0vVv6bEe+rbd6REPI+Ep8w43A8/wqc
    pB0q6j3Fs4FRlNUqshLaRN2HVbllb/+hlA1REOBGEvAuSHzXrThCS2PpEY8Ds7IG
    0rSuEdzwCd3c+vk+pssgxmFHBDPDJUsKSgUCF5wzA4k42tK/sixSDJlPcVKZdRrY
    +8XgaruPdIMoIVZHXdeNvBtra1kYRxZbeCpe1zSOiLL/xjSWVYEFhiO7ZBuHRDrq
    gaJmQNZxzwEUrpLsN4QB4S3jVmCEZ9Rjp8hWuaShRBWwYjlfhKlRcdwCol/T7ODC
    oioO3wBapwvsaCS4gmkmdBtvIKvbr62PM2nh6QpJwpyv9LPEXM5ZV0BT3AK8DIK6
    ThH5+uRF0QgDXHWIR55Gmh2usJ6VluPWT+f81Q3lH/jxXJfagGOFEFHtyT0yo23M
    iazev6j9O2En+uDYLSWgQ7uN+cFYSdfjj1FRjsQ84e8CwNJ1nhiQ/HexMN8zwqDo
    6LboOQuGiCet+KggAg==
    -----END CERTIFICATE-----

.. note:: Be sure to follow the directory and naming structure for certificates. All our documentation examples and tools will assert this structure.

Registering an App
~~~~~~~~~~~~~~~~~~
After you've obtained your signed public certificate you can use it to register your app id on the App Store. To do that either use the :ref:`REST API <api-register-app>` or use the App Store's `register app web interface <https://apps.nextcloud.com/app/register>`_.

The interface will ask you for the following things:

* **Certificate**: Paste in the contents of your public certificate, e.g. **~/.nextcloud/certificates/news.crt**
* **Signature**: A signature over your app id to verify that you own the private certificate. Can be calculated by using the following command::

    echo -n "APP_ID" | openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key | openssl base64

  where **APP_ID** is your app's id, e.g::

    echo -n "news" | openssl dgst -sha512 -sign ~/.nextcloud/certificates/news.key | openssl base64

We will then verify the certificate and signature and register you as the app's owner. You are now able to publish releases.

Uploading an App Release
~~~~~~~~~~~~~~~~~~~~~~~~
After you've registered your app you can upload your app's releases to the App Store. To do that either use the :ref:`REST API <api-create-release>` or use the App Store's `upload app release web interface <https://apps.nextcloud.com/app/upload>`_.

The interface will ask you for the following things:

* **Download**: A download link to your app release archive (tar.gz)
* **Nightly**: Check if you are uploading a nightly release
* **Signature**: A signature over your release archive. Can be calculated by using the following command::

    openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key /path/to/app.tar.gz | openssl base64

  where **APP_ID** is your app's id, e.g::

    openssl dgst -sha512 -sign ~/.nextcloud/certificates/news.key /path/to/news.tar.gz | openssl base64

We then download the archive and verify the signature. In addition we try to verify and use as much information as possible form the archive, e.g.:

* The archive most only contain one top level folder consisting of lower case ASCII characters and underscores

* The archive must contain an **info.xml** file inside the **appinfo** directory which in turn is located in the top folder

* The info.xml is reformatted using XSLT to bring everything into the correct order (required for XSD 1.0) and unknown elements are dropped. Old elements are migrated to their new equivalents if possible. Afterwards we validate it using an XML Schema (see :ref:`info-schema`)

If everything went well the release is then either created or updated. The downloaded archive will be deleted from our server.

Revoking a Certificate
~~~~~~~~~~~~~~~~~~~~~~
If you've lost or leaked your private certificate you want to revoke your certificate.

You can revoke your previous certificate by either posting your public certificate and revocation request `on our issue tracker <https://github.com/nextcloud/appstore/issues/new>`_ or by requesting a new certificate for an already requested app id.

After you've obtained a new certificate, simply use it to register your app id again (only owners are allowed to do this). This will delete all previous releases from our server since their signature has become invalid.

.. _app-metadata:

App Metadata
------------

App metadata is currently only being read from the **appinfo/info.xml** file. Future releases might include further files like CHANGELOG.md and AUTHORS.md files.

The info.xml is validated using an XML Schema which can be accessed `online <https://apps.nextcloud.com/schema/apps/info.xsd>`_.

info.xml
~~~~~~~~
A minimum valid **info.xml** would look like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">
        <id>news</id>
        <name>News</name>
        <summary>An RSS/Atom feed reader</summary>
        <description>An RSS/Atom feed reader</description>
        <version>8.8.2</version>
        <licence>agpl</licence>
        <author>Bernhard Posselt</author>
        <category>multimedia</category>
        <dependencies>
            <!-- owncloud tag is required on Nextcloud 9, 10 and 11 -->
            <owncloud min-version="9.1"/>
            <nextcloud min-version="10"/>
        </dependencies>
    </info>

A full blown example would look like this (needs to be utf-8 encoded):

.. code-block:: xml

    <?xml version="1.0"?>
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">
        <id>news</id>
        <name lang="de">Nachrichten</name>
        <name>News</name>
        <summary lang="en">An RSS/Atom feed reader</summary>
        <description lang="en"># Description\nAn RSS/Atom feed reader</description>
        <description lang="de"><![CDATA[# Beschreibung\nEine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann]]></description>
        <version>8.8.2</version>
        <licence>agpl</licence>
        <author mail="mail@provider.com" homepage="http://example.com">Bernhard Posselt</author>
        <author>Alessandro Cosentino</author>
        <author>Jan-Christoph Borchardt</author>
        <documentation>
            <user>https://github.com/owncloud/news/wiki#user-documentation</user>
            <admin>https://github.com/owncloud/news#readme</admin>
            <developer>https://github.com/owncloud/news/wiki#developer-documentation</developer>
        </documentation>
        <category>multimedia</category>
        <category>tools</category>
        <website>https://github.com/owncloud/news</website>
        <bugs>https://github.com/owncloud/news/issues</bugs>
        <repository>https://github.com/owncloud/news</repository>
        <discussion>https://help.nextcloud.com/t/nextcloud-conference-in-berlin-sept-16-22/1710</discussion>
        <screenshot>https://example.com/1.png</screenshot>
        <screenshot>https://example.com/2.jpg</screenshot>
        <dependencies>
            <php min-version="5.6" min-int-size="64"/>
            <database min-version="9.4">pgsql</database>
            <database>sqlite</database>
            <database min-version="5.5">mysql</database>
            <command>grep</command>
            <command>ls</command>
            <lib min-version="2.7.8">libxml</lib>
            <lib>curl</lib>
            <lib>SimpleXML</lib>
            <lib>iconv</lib>
            <!-- owncloud tag is required on Nextcloud 9, 10 and 11 -->
            <owncloud min-version="9.0" max-version="9.1"/>
            <nextcloud min-version="9" max-version="10"/>
        </dependencies>
        <background-jobs>
            <job>OCA\DAV\CardDAV\Sync\SyncJob</job>
        </background-jobs>
        <repair-steps>
            <pre-migration>
                <step>OCA\DAV\Migration\Classification</step>
            </pre-migration>
            <post-migration>
                <step>OCA\DAV\Migration\Classification</step>
            </post-migration>
            <live-migration>
                <step>OCA\DAV\Migration\GenerateBirthdays</step>
            </live-migration>
            <install>
                <step>OCA\DAV\Migration\GenerateBirthdays</step>
            </install>
            <uninstall>
                <step>OCA\DAV\Migration\GenerateBirthdays</step>
            </uninstall>
        </repair-steps>
        <two-factor-providers>
            <provider>OCA\AuthF\TwoFactor\Provider</provider>
        </two-factor-providers>
        <commands>
            <command>A\Php\Class</command>
        </commands>
    </info>

The following tags are validated and used in the following way:

id
    * required
    * must contain only lowercase ASCII characters and underscore
    * must match the first folder in the archive
    * will be used to identify the app
name
    * required
    * must occur at least once with **lang="en"** or no lang attribute
    * can be translated by using multiple elements with different **lang** attribute values, language code needs to be set **lang** attribute
    * will be rendered on the app detail page
summary
    * optional
    * if not provided the description element's text will be used
    * must occur at least once with **lang="en"** or no lang attribute
    * can be translated by using multiple elements with different **lang** attribute values, language code needs to be set **lang** attribute
    * will be rendered on the app list page as short description
description
    * required
    * must occur at least once with **lang="en"** or no lang attribute
    * can contain Markdown
    * can be translated by using multiple elements with different **lang** attribute values, language code needs to be set **lang** attribute
    * will be rendered on the app detail page
version
    * required
    * must be a `semantic version <http://semver.org/>`_, digits only
    * will be padded to a version with three numbers (e.g. 9 will be padded to 9.0.0)
licence
    * required
    * must contain **agpl** as the only valid value
author
    * required
    * can occur multiple times with different authors
    * can contain a **mail** attribute which must be an email
    * can contain a **homepage** which must be an URL
    * will not (yet) be rendered on the App Store
    * will be provided through the REST API
documentation/user
    * optional
    * must contain an URL to the user documentation
    * will be rendered on the app detail page
documentation/admin
    * optional
    * must contain an URL to the admin documentation
    * will be rendered on the app detail page
documentation/developer
    * optional
    * must contain an URL to the developer documentation
    * will be rendered on the app detail page
category
    * optional
    * if not provided the category **tools** will be used
    * must contain one of the following values:

       * **auth**
       * **customization**
       * **files**
       * **integration**
       * **monitoring**
       * **multimedia**
       * **office**
       * **organization**
       * **social**
       * **tools**

    * old categories are migrated:

       * **tool**, **game** and **other** will be converted to **tools**
       * **productivity** will be converted to **organization**

    * can occur more than once with different categories
website
    * optional
    * must contain an URL to the project's homepage
    * will be rendered on the app detail page
bugs
    * optional
    * must contain an URL to the project's bug tracker
    * will be rendered on the app detail page
repository
    * optional
    * must contain an URL to the project's repository
    * can contain a **type** attribute, **git**, **mercurial**, **subversion** and **bzr** are allowed values, defaults to **git**
    * currently not used
discussion
    * optional
    * must contain an URL to the forum, starting with https://help.nextcloud.com
    * will be rendered on the app detail page
screenshot
    * optional
    * must contain an HTTPS URL to an image
    * will be rendered on the app list and detail page in the given order
dependencies/php
    * optional
    * can contain a **min-version** attribute (maximum 3 digits separated by dots)
    * can contain a **max-version** attribute (maximum 3 digits separated by dots)
    * can contain a **min-int-size** attribute, 32 or 64 are allowed as valid values
    * will be rendered on the app releases page
dependencies/database
    * optional
    * must contain the database name as text, **sqlite**, **pgsql** and **mysql** are allowed as valid values
    * can occur multiple times with different databases
    * can contain a **min-version** attribute (maximum 3 digits separated by dots)
    * can contain a **max-version** attribute (maximum 3 digits separated by dots)
    * will be rendered on the app releases page
dependencies/command
    * optional
    * must contain a linux command as text value
    * can occur multiple times with different commands
    * will be rendered on the app releases page
dependencies/lib
    * optional
    * will be rendered on the app releases page
    * must contain a required php extension
    * can occur multiple times with different php extensions
    * can contain a **min-version** attribute (maximum 3 digits separated by dots)
    * can contain a **max-version** attribute (maximum 3 digits separated by dots)
dependencies/nextcloud
    * required on Nextcloud 12 or higher
    * if absent white-listed owncloud versions will be taken from the owncloud element (see below)
    * must contain a **min-version** attribute (maximum 3 digits separated by dots)
    * can contain a **max-version** attribute (maximum 3 digits separated by dots)
dependencies/owncloud
    * optional
    * used for app migration period (Nextcloud 9, 10 and 11)
    * must contain a **min-version** attribute (**9.0**, **9.1** or **9.2**)
    * can contain a **max-version** attribute (**9.0**, **9.1** or **9.2**)
    * will be ignored if a **nextcloud** tag exists
    * 9.0 will be migrated to Nextcloud 9
    * 9.1 will be migrated to Nextcloud 10
    * 9.2 will be migrated to Nextcloud 11
    * All other versions will be ignored
background-jobs/job
    * optional
    * must contain a php class which is run as background jobs
    * will not be used, only validated
repair-steps/pre-migration/step
    * optional
    * must contain a php class which is run before executing database migrations
    * will not be used, only validated
repair-steps/post-migration/step
    * optional
    * must contain a php class which is run after executing database migrations
    * will not be used, only validated
repair-steps/live-migration/step
    * optional
    * must contain a php class which is run after executing post-migration jobs
    * will not be used, only validated
repair-steps/install/step
    * optional
    * must contain a php class which is run after installing the app
    * will not be used, only validated
repair-steps/uninstall/step
    * optional
    * must contain a php class which is run after uninstalling the app
    * will not be used, only validated
two-factor-providers/provider
    * optional
    * must contain a php class which is registered as two factor auth provider
    * will not be used, only validated
commands/command
    * optional
    * must contain a php class which is registered as occ command
    * will not be used, only validated

The following character maximum lengths are enforced:

* All description Strings are database text fields and therefore not limited in size
* All other Strings have a maximum of 256 characters

The following elements are either deprecated or for internal use only and will fail the validation if present:

* **standalone**
* **default_enable**
* **shipped**
* **public**
* **remote**
* **requiremin**
* **requiremax**


.. _info-schema:

Schema Integration
------------------
We provide an XML schema for the info.xml file which is available under `https://apps.nextcloud.com/schema/apps/info.xsd <https://apps.nextcloud.com/schema/apps/info.xsd>`_ and can be used to validate your info.xml or provide autocompletion in your IDE.

You can validate your info.xml using `various online tools <http://www.utilities-online.info/xsdvalidation/>`_

Various IDEs automatically validate and auto complete XML elements and attributes if you add the schema in your info.xml like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">

          <!-- content here -->

    </info>

