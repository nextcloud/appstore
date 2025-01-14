.. _developer-guide:

App Developer Guide
===================

Note: Documentation and a tutorial about App Development itself (vs "app development and the App Store") is found at
`https://docs.nextcloud.com/server/stable/developer_manual/app_development/index.html <https://docs.nextcloud.com/server/stable/developer_manual/app_development/index.html>`_.
Information regarding app monetization and payment can be found at
`https://docs.nextcloud.com/server/latest/developer_manual/app_publishing_maintenance/monetizing.html <https://docs.nextcloud.com/server/latest/developer_manual/app_publishing_maintenance/monetizing.html>`_.

Most of today's developers publish their source code on GitHub, BitBucket, GitLab or on their own GitLab instance. These tools typically also provide a way to release new versions based on Git tags or by uploading custom archives.

Experienced users and package maintainers typically prefer to download the app directly from these services whereas administrators or novice users look for app releases on the App Store. This means that you have to take care of publishing two releases on two different platforms.

We want to avoid duplication and make it harder to ship broken releases by mistake, therefore we went for the following solution:

* Your app's source code is hosted on GitHub or a similar service

* You should use Git tags to create new releases on these services

* GitHub release downloads do not match the required folders structure. This is because GitHub appends a version to the top folder name. Therefore you need to create a separate release which conforms to the expected structure.

This keeps your repository up to date and satisfies the needs of maintainers, developers and experienced users.

Publishing Apps on the App Store
--------------------------------
Hosting the archive on a different host means of course that we can not guarantee that the contents have not been tampered with. Neither can we guarantee that the actual app developer uploaded the app. Therefore we require you to sign your app using a certificate.

Obtaining a Certificate
~~~~~~~~~~~~~~~~~~~~~~~
The certificates should be stored in **~/.nextcloud/certificates/** so first create the folder if it does not exist yet::

    mkdir -p ~/.nextcloud/certificates/

Then change into the directory::

    cd ~/.nextcloud/certificates/

and generate your private key and CSR::

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


.. _app-register:

Registering an App
~~~~~~~~~~~~~~~~~~
After you've obtained your signed public certificate you can use it to register your app id on the App Store. To do that either use the :ref:`REST API <api-register-app>` or use the App Store's `register app web interface <https://apps.nextcloud.com/developer/apps/new>`_.

The interface will ask you for the following things:

* **Certificate**: Paste in the contents of your public certificate, e.g. **~/.nextcloud/certificates/news.crt**
* **Signature**: A signature over your app id to verify that you own the private certificate. Can be calculated by using the following command::

    echo -n "APP_ID" | openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key | openssl base64

  where **APP_ID** is your app's id, e.g::

    echo -n "news" | openssl dgst -sha512 -sign ~/.nextcloud/certificates/news.key | openssl base64

We will then verify the certificate and signature and register you as the app's owner. You are now able to publish releases.

.. _uploading_a_release:

Uploading an App Release
~~~~~~~~~~~~~~~~~~~~~~~~
After you've registered your app you can upload your app's releases to the App Store. To do that either use the :ref:`REST API <api-create-release>` or use the App Store's `upload app release web interface <https://apps.nextcloud.com/developer/apps/releases/new>`_.

The interface will ask you for the following things:

* **Download**: A download link to your app release archive (tar.gz)
* **Nightly**: Check if you are uploading a nightly release
* **Signature**: A signature over your release archive. Can be calculated by using the following command::

    openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key /path/to/app.tar.gz | openssl base64

  where **APP_ID** is your app's id, e.g::

    openssl dgst -sha512 -sign ~/.nextcloud/certificates/news.key /path/to/news.tar.gz | openssl base64

We then download the archive and verify the signature. In addition we try to verify and use as much information as possible form the archive, e.g.:

* The archive must only contain one top level folder consisting of lower case ASCII characters and underscores

* The archive must contain an **info.xml** file inside the **appinfo** directory which in turn is located in the top folder

* The info.xml is reformatted using XSLT to bring everything into the correct order (required for XSD 1.0) and unknown elements are dropped. Old elements are migrated to their new equivalents if possible. Afterwards we validate it using an XML Schema (see :ref:`info-schema`)

If everything went well the release is then either created or updated. The downloaded archive will be deleted from our server.

.. _app-revoke-cert:

Updating and Revoking a Certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you've lost or leaked your private certificate you want to revoke and update your certificate:

* Send a pull request with the new CSR for an already existing app `to our repository <hhttps://github.com/nextcloud/app-certificate-requests>`_ (overwrite the existing file, e.g. news/news.csr and delete the existing news/news.crt)
* We will revoke your old certificate and sign your new certificate request
* Then re-register your app certificate on the `app register page <https://apps.nextcloud.com/developer/apps/new>`_. This will delete all existing releases.


After you've obtained a new certificate, simply use it to register your app id again (only owners are allowed to do this). This will delete all previous releases from our server since their signature has become invalid.

Transferring Your App to a New Owner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transferring an app works similar to :ref:`registering an app <app-register>`: The new owner simply needs to register the app again using the public certificate and the signature.

However by default this is restricted to the app's owner. To disable this restriction you first need to unlock your app for the owner transfer. You can do this by going to your **account** settings and choosing `Transfer app ownership <https://apps.nextcloud.com/account/transfer-apps>`_. On that page you can lock or unlock your apps for being transferred.

After you unlocked your app for transfer, the new owner can then proceed to register the app again. If everything went fine the app is now transferred to the new owner and the transfer setting for that app is locked again.


.. _app-metadata:

App Metadata
------------

App metadata is currently being read from the **appinfo/info.xml** and **CHANGELOG.md** file.

info.xml
~~~~~~~~
The info.xml is validated using an XML Schema which can be accessed `online <https://apps.nextcloud.com/schema/apps/info.xsd>`_.

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
        <licence>AGPL-3.0-or-later</licence>
        <author>Bernhard Posselt</author>
        <category>multimedia</category>
        <bugs>https://github.com/nextcloud/news/issues</bugs>
        <dependencies>
            <nextcloud min-version="31"/>
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
        <licence>AGPL-3.0-or-later</licence>
        <author mail="mail@provider.com" homepage="http://example.com">Bernhard Posselt</author>
        <author>Alessandro Cosentino</author>
        <author>Jan-Christoph Borchardt</author>
        <documentation>
            <user>https://github.com/nextcloud/news/wiki#user-documentation</user>
            <admin>https://github.com/nextcloud/news#readme</admin>
            <developer>https://github.com/nextcloud/news/wiki#developer-documentation</developer>
        </documentation>
        <category>multimedia</category>
        <category>tools</category>
        <website>https://github.com/nextcloud/news</website>
        <discussion>https://your.forum.com</discussion>
        <bugs>https://github.com/nextcloud/news/issues</bugs>
        <repository>https://github.com/nextcloud/news</repository>
        <screenshot small-thumbnail="https://example.com/1-small.png">https://example.com/1.png</screenshot>
        <screenshot>https://example.com/2.jpg</screenshot>
        <donation type="paypal" title="Donate via PayPal">https://paypal.com/example-link</donation>
        <donation>https://github.com/sponsors/example</donation>
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
            <nextcloud min-version="31" max-version="32"/>
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
        <settings>
            <admin>OCA\Theming\Settings\Admin</admin>
            <admin-section>OCA\Theming\Settings\Section</admin-section>
            <personal>OCA\Theming\Settings\Personal</personal>
            <personal-section>OCA\Theming\Settings\PersonalSection</personal-section>
        </settings>
        <activity>
            <settings>
                <setting>OCA\Files\Activity\Settings\FavoriteAction</setting>
                <setting>OCA\Files\Activity\Settings\FileChanged</setting>
                <setting>OCA\Files\Activity\Settings\FileCreated</setting>
                <setting>OCA\Files\Activity\Settings\FileDeleted</setting>
                <setting>OCA\Files\Activity\Settings\FileFavorite</setting>
                <setting>OCA\Files\Activity\Settings\FileRestored</setting>
            </settings>

            <filters>
                <filter>OCA\Files\Activity\Filter\FileChanges</filter>
                <filter>OCA\Files\Activity\Filter\Favorites</filter>
            </filters>

            <providers>
                <provider>OCA\Files\Activity\FavoriteProvider</provider>
                <provider>OCA\Files\Activity\Provider</provider>
            </providers>
        </activity>
        <navigations>
            <navigation role="admin">
                <id>files</id>
                <name>Files</name>
                <route>files.view.index</route>
                <order>0</order>
                <icon>app.svg</icon>
                <type>link</type>
            </navigation>
        </navigations>
        <collaboration>
            <plugins>
                <plugin type="collaborator-search" share-type="SHARE_TYPE_CIRCLE">OCA\Circles\Collaboration\v1\CollaboratorSearchPlugin</plugin>
                <plugin type="autocomplete-sort">OCA\Circles\Collaboration\v1\CircleSorter</plugin>
            </plugins>
        </collaboration>
        <sabre>
            <collections>
                <collection>\OCA\Deck\Dav\RootCollection</collection>
            </collections>
            <plugins>
                <plugin>\OCA\Deck\Dav\ServerPlugin</plugin>
            </plugins>
        </sabre>
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
    * must be a `semantic version <http://semver.org/>`_ without build metadata, e.g. 9.0.1 or 9.1.0-alpha.1
licence
    * required
    * can occur multiple times with different licenses
    * must contain one of the following licenses (see the `SPDX License List <https://spdx.org/licenses/>`_ for details):

        * **AGPL-3.0-only**
        * **AGPL-3.0-or-later**
        * **Apache-2.0**
        * **GPL-3.0-only**
        * **GPL-3.0-or-later**
        * **MIT**
        * **MPL-2.0**

    * (deprecated) the following shorthand aliases are also used:

        * **agpl** (AGPL-3.0)
        * **apache** (Apache-2.0)
        * **gpl3** (GPL-3.0)
        * **mit** (MIT)
        * **mpl** (MPL-2.0)

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

       * **customization**
       * **dashboard**
       * **files**
       * **games**
       * **search**
       * **integration**
       * **monitoring**
       * **multimedia**
       * **office**
       * **organization**
       * **security**
       * **social**
       * **tools**
       * **workflow**

    * old categories are migrated:

       * **auth** will be converted to **security**

    * can occur more than once with different categories
website
    * optional
    * must contain an URL to the project's homepage
    * will be rendered on the app detail page
discussion
    * optional
    * must contain an URL to the project's discussion page/forum
    * will be rendered on the app detail page as the "ask question or discuss" button
    * if absent, it will default to our forum at https://help.nextcloud.com/ and create a new category in the apps category
bugs
    * required
    * must contain an URL to the project's bug tracker
    * will be rendered on the app detail page
repository
    * optional
    * must contain an URL to the project's repository
    * can contain a **type** attribute, **git**, **mercurial**, **subversion** and **bzr** are allowed values, defaults to **git**
    * currently not used
screenshot
    * optional
    * must contain an HTTPS URL to an image
    * can contain a **small-thumbnail** attribute which must contain an https url to an image. This image will be used as small preview (e.g. on the app list overview). Keep it small so it renders fast
    * will be rendered on the app list and detail page in the given order
donation
    * optional
    * can occur multiple times containing different donation URLs
    * can contain a **title** attribute which must be a string, defaults to **Donate to support this app**
    * can contain a **type** attribute, **paypal**, **stripe**, and **other** are allowed values, defaults to **other**
    * will be rendered on the app detail page in the given order
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
    * required on Nextcloud 11 or higher
    * if absent white-listed owncloud versions will be taken from the owncloud element (see below)
    * must contain a **min-version** attribute (maximum 3 digits separated by dots)
    * can contain a **max-version** attribute (maximum 3 digits separated by dots)
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
activity/settings/setting
    * optional
    * must contain a php class which implements OCP\Activity\ISetting and is used to add additional settings ui elements to the activity app
activity/filters/filter
    * optional
    * must contain a php class which implements OCP\Activity\IFilter and is used to add additional filters to the activity app
activity/providers/provider
    * optional
    * must contain a php class which implements OCP\Activity\IProvider and is used to react to events from the activity app
settings/admin
    * optional
    * must contain a php class which implements OCP\Settings\ISettings and returns the form to render for the global settings area
settings/admin-section
    * optional
    * must contain a php class which implements OCP\Settings\ISection and returns data to render navigation entries in the global settings area
settings/personal
    * optional
    * must contain a php class which implements OCP\Settings\ISettings and returns the form to render for the global settings area
settings/personal-section
    * optional
    * must contain a php class which implements OCP\Settings\ISection and returns data to render navigation entries in the global settings area
navigations
    * optional
    * must contain at least one navigation element
navigations/navigation
    * required
    * must contain a name and route element
    * denotes a navigation entry
    * role denotes the visibility, all means everyone can see it, admin means only an admin can see the navigation entry, defaults to all
navigations/navigation/id
    * optional
    * the app id
    * you can also create entries for other apps by setting an id other than your app one's
navigations/navigation/name
    * required
    * will be displayed below the navigation entry icon
    * will be translated by the default translation tools
navigations/navigation/route
    * required
    * name of the route that will be used to generate the link
navigations/navigation/icon
    * optional
    * name of the icon which is looked up in the app's **img/** folder
    * defaults to app.svg
navigations/navigation/order
    * optional
    * used to sort the navigation entries
    * a higher order number means that the entry will be ordered further to the bottom
navigations/navigation/type
    * optional
    * can be either link or settings
    * link means that the entry is added to the default app menu
    * settings means that the entry is added to the right-side menu which also contains the personal, admin, users, help and logout entry
collaboration
    * optional
    * can contain plugins for collaboration search (e.g. supplying share dialog)
collaboration/plugins
    * optional
    * must contain at least one plugin
collaboration/plugins/plugin
    * required
    * the PHP class name of the plugin
    * must contain **type** attribute which can be
        * *collaboration-search* (The class must implement OCP\Collaboration\Collaborators\ISearchPlugin), requires **share-type** attribute
        * *autocomplete-sort* (The class must implement OCP\Collaboration\AutoComplete\ISorter)
    * optionally contain **share-type** attribute
sabre
    * optional
    * can contain plugins or collections to be loaded by the dav app
sabre/plugins
    * optional
    * must contain at least one plugin
    * A sabre plugin extend the dav system by adding additional event handlers. For mor details see http://sabre.io/dav/writing-plugins/
sabre/plugins/plugin
    * required
    * the PHP class name of the plugin
sabre/collections
    * optional
    * must contain at least one collection
    * Collections allow apps to expose their own directory tree to the dav endpoint. They will be added to the root of the Nextcloud dav tree.
sabre/collections/collection
    * required
    * the PHP class name of the plugin
    * classes must implement the Sabre\DAV\ICollection interface

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


database.xml
~~~~~~~~~~~~
The database.xml is validated using an XML Schema which can be accessed `through the App Store <https://apps.nextcloud.com/schema/apps/database.xsd>`_.

A minimum valid **database.xml** would look like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/database.xsd">
        <table>
            <name>*dbprefix*blog_articles</name>
            <declaration>

            </declaration>
        </table>
    </database>

A full blown example would look like this (needs to be utf-8 encoded):

.. code-block:: xml

    <?xml version="1.0"?>
    <database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/database.xsd">
        <table>
            <name>*dbprefix*blog_articles</name>
            <declaration>
                <field>
                    <name>id</name>
                    <type>integer</type>
                    <length>8</length>
                    <unsigned>true</unsigned>
                    <notnull>true</notnull>
                    <autoincrement>true</autoincrement>
                </field>
                <field>
                    <name>user</name>
                    <type>text</type>
                    <length>255</length>
                    <notnull>true</notnull>
                    <default>anonymous</default>
                </field>
                <field>
                    <name>donations_in_euros</name>
                    <type>decimal</type>
                    <default>0.00</default>
                    <precision>12</precision>
                    <scale>2</scale>
                </field>
                <index>
                    <name>blog_articles_id_user_index</name>
                    <primary>true</primary>
                    <unique>true</unique>
                    <field>
                        <name>id</name>
                    </field>
                    <field>
                        <name>user</name>
                    </field>
                </index>
                <index>
                    <name>blog_articles_user_index</name>
                    <field>
                        <name>user</name>
                    </field>
                </index>
            </declaration>
        </table>
    </database>

.. note:: While you might encounter valid elements like **create**, **overwrite**, **charset** or **sorting** they are not parsed by Nextcloud and can therefore be omitted safely

Changelog
~~~~~~~~~

The changelog has to be named **CHANGELOG.md** and being placed in your app's top level folder, e.g. **news/CHANGELOG.md**.

Changelogs have to follow the `Keep a CHANGELOG format <http://keepachangelog.com>`_, e.g.::

    ## [Unreleased]
    ### Added
    - Nighly changes here

    ## 0.6.0 – 2016-09-20
    ### Added
    - Alias support
      [#1523](https://github.com/owncloud/mail/pull/1523) @tahaalibra
    - New incoming messages are prefetched
      [#1631](https://github.com/owncloud/mail/pull/1631) @ChristophWurst
    - Custom app folder support
      [#1627](https://github.com/owncloud/mail/pull/1627) @juliushaertl
    - Improved search
      [#1609](https://github.com/owncloud/mail/pull/1609) @ChristophWurst
    - Scroll to refresh
      [#1595](https://github.com/owncloud/mail/pull/1593) @ChristophWurst
    - Shortcuts to star and mark messages as unread
      [#1590](https://github.com/owncloud/mail/pull/1590) @ChristophWurst
    - Shortcuts to select previous/next messsage
      [#1557](https://github.com/owncloud/mail/pull/1557) @ChristophWurst

    ### Changed
    - Minimum server is Nextcloud 10/ownCloud 9.1
      [#84](https://github.com/nextcloud/mail/pull/84) @ChristophWurst
    - Use session storage instead of local storage for client-side cache
      [#1612](https://github.com/owncloud/mail/pull/1612) @ChristophWurst
    - When deleting the current message, the next one is selected immediatelly
      [#1585](https://github.com/owncloud/mail/pull/1585) @ChristophWurst

    ### Fixed
    - Client error while composing a new message
      [#1609](https://github.com/owncloud/mail/pull/1609) @ChristophWurst
    - Delay app start until page has finished loading
      [#1634](https://github.com/owncloud/mail/pull/1634) @ChristophWurst
    - Auto-redirection of HTML mail links
      [#1603](https://github.com/owncloud/mail/pull/1603) @ChristophWurst
    - Update folder counters when reading/deleting messages
      [#1585](https://github.com/owncloud/mail/pull/1585)

    ### Removed
    - Removed old API

    ### Deprecated
    - Deprecated new API

    ### Security
    - Fixed XXE in xml upload

.. note:: The regex for matching the line is **^## (\\d+\\.\\d+\\.\\d+)**, the regex for nightlies and pre-releases is **^## [Unreleased]**

The version has to be equal to the version in your info.xml. If the parser can't find a changelog entry, it will be set to an empty string. Only the changelog for the current release will be imported.

The changelog for nightlies and pre-releases will be taken from the **## [Unreleased]** block

Changelogs can be translated as well. To add a changelog for a specific translation, use **CHANGELOG.code.md**, e.g.: **CHANGELOG.fr.md**


Blacklisted Files
-----------------

To prevent you from nuking your local app's version control directory all uploaded archives are validated to not contain the following folders:

* **.git**


.. _info-schema:

Schema Integration
------------------
We provide an XML schema which can be used to validate and get IDE autocompletion for the following files:

* **appinfo/info.xml**:

    .. code-block:: xml

        <?xml version="1.0"?>
        <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">

              <!-- content here -->

        </info>

* **appinfo/database.xml**:

    .. code-block:: xml

        <?xml version="1.0"?>
        <database xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/database.xsd">

              <!-- content here -->

        </database>

You can also validate your info.xml using `various online tools <http://www.utilities-online.info/xsdvalidation/>`_
