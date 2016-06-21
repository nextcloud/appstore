REST API
========

A REST API for publishing and deleting app releases has been built into the store from day one to help release automation.

Intended Developer Workflow
---------------------------

Most of today's developers publish their source code on GitHub, BitBucket or on their own GitLab instance. These tools typically also provide a way to release new versions based on Git tags or by uploading custom archives.

Advanced users and developers typically prefer to download the app directly from these services whereas administrators or novice users look for app releases on the app store. This means that you have to take care of publishing two releases on two different platforms.

We want to avoid duplication and make it harder to ship broken releases by mistake, therefore we went for the following solution:

* Your app's source code is hosted on GitHub or a similar service

* You should use Git tags to create new releases on these services

* Archives are typically created automatically for you. If you require compilation or other transformations like minification, you should upload a pre-built archive to the appropriate releases page

This keeps your repository up to date and satisfies the needs of developers and advanced users.

To publish an app release on the app store you simply send us a download link for the release archive. We then do the following:

* Your archive is downloaded from the given location. This ensures that your users don't hit dead links. If your archive is too big, we will abort the download.

* The archive is then extracted and the package structure is validated:

 * The archive most only contain one top level folder consisting of lower case ASCII characters and underscores
 * The archive must contain an **info.xml** file inside the **appinfo** directory which in turn is located in the top folder

* The app's metadata is then extracted from the **info.xml** file and validated using an XML Schema (available under `https://apps.nextcloud.com/info.xsd <https://apps.nextcloud.com/info.xsd>`_):

 * The app folder must match the id
 * The specified versions must have 1 to 3 digits separated by dots
 * The XML elements must contain valid content (e.g. known categories and enumerations)

* The release is then either created or updated. The downloaded archive will be deleted

Since this implies that the download location must be trusted, the following mechanisms are in place to guarantee that the downloaded version has not been tampered with:

* You can submit a sha256sum hash in addition to the download link. The hash is validated on the user's server when he installs it. If you omit the hash, we generate it from the downloaded archive

* You can sign your code `using a certificate <https://docs.nextcloud.org/server/9/developer_manual/app/code_signing.html>`_

* You must supply an HTTPS download url for the archive

Specification
-------------

The following API routes are present:

* :ref:`api-all-releases`

* :ref:`api-delete-app`

* :ref:`api-delete-release`

* :ref:`api-create-release`

.. _api-all-releases:

Get All Apps and Releases
~~~~~~~~~~~~~~~~~~~~~~~~~
This route will return all releases to display inside Nextcloud's apps admin area.

* **Url**: GET /api/v1/platform/{**platform-version**}/apps.json
* **Url parameters**:

  * **platform-version**: semantic version, digits only: Returns all the apps and their releases that work on this version. If an app has no working releases, the app will be excluded

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl http://localhost:8000/api/v1/platform/9.0.0/apps.json -H 'If-None-Match: "1-1-2016-06-17 23:08:58.042321+00:00"'

* **Returns**: application/json

.. code-block:: json

    [
        {
            "id": "news",
            "categories": [
                {
                    "id": "tools",
                    "translations": {
                        "en": {
                            "name": "Tools"
                        },
                        "de": {
                            "name": "Werkzeuge"
                        },
                        "fr": {
                            "name": "Outil"
                        }
                    }
                }
            ],
            "recommendations": 100,
            "userDocs": "http://127.0.0.1:8000/user",
            "adminDocs": "http://127.0.0.1:8000/admin",
            "developerDocs": "http://127.0.0.1:8000/dev",
            "issueTracker": "http://127.0.0.1:8000/issue",
            "website": "http://127.0.0.1:8000/",
            "created": "2016-06-09T17:56:05.076980Z",
            "lastModified": "2016-06-09T17:56:19.099038Z",
            "releases": [
                {
                    "version": "1.9.0",
                    "checksum": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15",
                    "phpExtensions": [
                        {
                            "id": "libxml",
                            "versionSpec": ">=3.0.0 <5.0.0"
                        }
                    ],
                    "databases": [
                        {
                            "id": "sqlite",
                            "name": "Sqlite",
                            "versionSpec": "*"
                        }
                    ],
                    "shellCommands": [
                        "grep"
                    ],
                    "phpVersionSpec": "<7.0.0",
                    "platformVersionSpec": ">=9.0.0",
                    "minIntSize": 64,
                    "download": "https://127.0.0.1:8000/download",
                    "created": "2016-06-09T17:57:00.587076Z",
                    "lastModified": "2016-06-09T17:57:00.587238Z"
                }
            ],
            "licenses": [
                  {
                      "id": "agpl",
                      "name": "AGPLv3+"
                  }
            ],
            "screenshots": [
                {
                    "url": "http://feeds2.feedburner.com/blogerator"
                }
            ],
            "translations": {
                "en": {
                    "name": "News",
                    "description": "Read News"
                },
                "de": {
                    "name": "Neuigkeiten",
                    "description": "Nachrichten lesen"
                }
            }
        }
    ]

translations
    Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.

versionSpec
    Required versions (minimum and maximum versions) are transformed to semantic version specs. If a field is a \*, this means that there is no version requirement. The following permutations can occur:

     * **All versions**: \*
     * **Maximum version only**: <8.1.2
     * **Minimum version only**: >=9.3.2
     * **Maximum and minimum version**: >=9.3.2 <8.1.2

checksum
    The checksum is generated by running sha256sum over the downloaded archive.

recommendations
    Who many users recommend the app

.. _api-delete-app:

Delete an App
~~~~~~~~~~~~~
Only app owners are allowed to delete an app. The owner is the user that pushes the first release of an app to the store.

Deleting an app will also delete all releases which are associated with it.

* **Url**: DELETE /api/v1/apps/{**app-id**}

* **Url parameters**:

 * **app-id**: app id, lower case ASCII characters and underscores are allowed

* **Authentication**: Basic

* **Authorization**: App owners

* **Example CURL request**::

    curl -X DELETE http://localhost:8000/api/v1/apps/news -u "user:password"


* **Returns**:

 * **HTTP 204**: If the app was deleted successfully
 * **HTTP 401**: If the user is not authenticated
 * **HTTP 403**: If the user is not authorized to delete the app
 * **HTTP 404**: If the app could not be found

.. _api-delete-release:

Delete an App Release
~~~~~~~~~~~~~~~~~~~~~
Only app owners or co-maintainers are allowed to delete an app release. The owner is the user that pushes the first release of an app to the store.

* **Url**: DELETE /api/v1/apps/{**app-id**}/releases/{**app-version**}

* **Url parameters**:

 * **app-id**: app id, lower case ASCII characters and underscores are allowed
 * **app-version**: app version, semantic version, digits only

* **Authentication**: Basic

* **Authorization**: App owners and co-maintainers

* **Example CURL request**::

    curl -X DELETE http://localhost:8000/api/v1/apps/news/releases/9.0.0 -u "user:password"


* **Returns**:

  * **HTTP 204**: If the app release was deleted successfully
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app release
  * **HTTP 404**: If the app release could not be found


.. _api-create-release:

Publish a New App Release
~~~~~~~~~~~~~~~~~~~~~~~~~
The following request will create a new app release:

* **Url**: POST /api/v1/apps/releases

* **Authentication** Basic

* **Content-Type**: application/json

* **Request body**:

  * **download**: An Https (Http is not allowed!) link to the archive packaged (maximum size: 20 Megabytes) as tar.gz, info.xml must be smaller than 512Kb
  * **checksum (Optional)**: If not given we will calculate the sha256sum on the downloaded archive. If you are paranoid or host your packages on a host that you don't trust, you can supply your own sha256sum which can be generated by running::

      sha256sum release.tar.gz

  .. code-block:: json

      {
          "download": "https://example.com/release.tar.gz",
          "checksum": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15"
      }


* **Example CURL request**::

        curl -X POST -u "user:password" http://localhost:8000/api/v1/apps/releases -H "Content-Type: application/json" -d '{"download":"https://example.com/release.tar.gz"}'

* **Returns**:

  * **HTTP 200**: If the app release was update successfully
  * **HTTP 201**: If the app release was created successfully
  * **HTTP 400**: If the app contains invalid data, is too large or could not be downloaded
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app release

If there is no app with the given app id yet, a new app is created and the owner is set in to the logged in user. Then the **info.xml** file which lies in the compressed archive's folder **app-id/appinfo/info.xml** is being parsed and validated. The validated result is then saved in the database. Both owners and co-maintainers are allowed to upload new releases.

A minimum valid **info.xml** would look like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <info>
        <id>news</id>
        <name>News</name>
        <description>An RSS/Atom feed reader</description>
        <author>Bernhard Posselt</author>
        <category>multimedia</category>
        <version>8.8.2</version>
        <licence>agpl</licence>
        <dependencies>
            <owncloud min-version="9.0"/>
        </dependencies>
    </info>

A full blown example would look like this (needs to be utf-8 encoded):

.. code-block:: xml

    <?xml version="1.0"?>
    <info>
        <id>news</id>

        <!-- translation can be done via the lang attribute, defaults to English -->
        <name lang="de">Nachrichten</name>
        <name>News</name>

        <!-- description tag allows Markdown -->
        <description lang="en">An RSS/Atom feed reader</description>
        <description lang="de"><![CDATA[Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann]]></description>

        <!-- semantic version, three digits separated by a dot -->
        <version>8.8.2</version>

        <!-- multiple licenses are possible too but must at least include the agpl -->
        <!-- possible values: agpl, mit -->
        <licence>mit</licence>
        <licence>agpl</licence>

        <author mail="mail@provider.com" homepage="http://example.com">Bernhard Posselt</author>
        <author>Alessandro Cosentino</author>
        <author>Jan-Christoph Borchardt</author>

        <!-- documentation -->
        <documentation>
            <user>https://github.com/owncloud/news/wiki#user-documentation</user>
            <admin>https://github.com/owncloud/news#readme</admin>
            <developer>https://github.com/owncloud/news/wiki#developer-documentation</developer>
        </documentation>

        <!-- multiple categories are also possible -->
        <!-- possible values: multimedia, tools, games, pim -->
        <category>multimedia</category>
        <category>tools</category>


        <website>https://github.com/owncloud/news</website>

        <!-- issue tracker -->
        <bugs>https://github.com/owncloud/news/issues</bugs>

        <!-- screenshots, can be multiple and will be displayed in order -->
        <!-- need to be served with https -->
        <screenshot>https://example.com/1.png</screenshot>
        <screenshot>https://example.com/2.jpg</screenshot>

        <!-- dependencies, all version attributes except for the ownCloud min-version are optional -->
        <dependencies>
            <php min-version="5.6" min-int-size="64"/>
            <!-- php extensions, uses the same names as composer -->
            <!-- supported databases and versions -->
            <database min-version="9.4">pgsql</database>
            <database>sqlite</database>
            <database min-version="5.5">mysql</database>

            <!-- command line tools -->
            <command>grep</command>
            <command>ls</command>

            <lib min-version="2.7.8">libxml</lib>
            <lib>curl</lib>
            <lib>SimpleXML</lib>
            <lib>iconv</lib>

            <!-- version numbers will be padded to three digits with 0 (min-version) and 2^64 (max-version) -->
            <owncloud min-version="9.0" max-version="9.1"/>
        </dependencies>

        <!-- further elements to test if parser ignores non defined fields -->
    </info>


The following character maximum lengths are enforced:

* All description Strings are (almost) of unlimited size
* All Url Strings have a maximum of 256 characters
* All other Strings have a maximum of 128 characters
