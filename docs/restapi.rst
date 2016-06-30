REST API
========

A REST API for publishing and deleting app releases has been built into the store from day one to help release automation.

All APIs can easily be used with :doc:`ncdev <ncdev>`

Authentication
--------------

Several routes require authentication. The following authentication methods are supported:

* **Basic**: Http header where **CREDENTIALS** is ``base64encode('user:password')``::

    Authorization: Basic CREDENTIALS

* **Basic**: Http header where **TOKEN** is a token which can be looked up in your profile::

    Authorization: Token TOKEN

Specification
-------------

The following API routes are present:

* :ref:`api-all-releases`

* :ref:`api-all-categories`

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
                "multimedia"
            ],
            "userDocs": "https://github.com/owncloud/news/wiki#user-documentation",
            "adminDocs": "https://github.com/owncloud/news#readme",
            "developerDocs": "https://github.com/owncloud/news/wiki#developer-documentation",
            "issueTracker": "https://github.com/owncloud/news/issues",
            "website": "https://github.com/owncloud/news",
            "created": "2016-06-25T16:08:56.794719Z",
            "lastModified": "2016-06-25T16:49:25.326855Z",
            "releases": [
                {
                    "version": "8.8.0",
                    "nightly": false,
                    "phpExtensions": [
                        {
                            "id": "SimpleXML",
                            "versionSpec": "*"
                        },
                        {
                            "id": "curl",
                            "versionSpec": "*"
                        },
                        {
                            "id": "iconv",
                            "versionSpec": "*"
                        },
                        {
                            "id": "libxml",
                            "versionSpec": ">=2.7.8"
                        }
                    ],
                    "databases": [
                        {
                            "id": "mysql",
                            "versionSpec": ">=5.5.0"
                        },
                        {
                            "id": "pgsql",
                            "versionSpec": ">=9.4.0"
                        },
                        {
                            "id": "sqlite",
                            "versionSpec": "*"
                        }
                    ],
                    "shellCommands": [
                        "grep"
                    ],
                    "phpVersionSpec": ">=5.6.0",
                    "platformVersionSpec": ">=9.0.0 <9.2.0",
                    "minIntSize": 64,
                    "download": "https://github.com/owncloud/news/releases/download/8.8.0/news.tar.gz",
                    "created": "2016-06-25T16:08:56.796646Z",
                    "licenses": [
                        "agpl"
                    ],
                    "lastModified": "2016-06-25T16:49:25.319425Z",
                    "checksum": "909377e1a695bbaa415c10ae087ae1cc48e88066d20a5a7a8beed149e9fad3d5"
                }
            ],
            "screenshots": [
                {
                    "url": "https://example.com/news.jpg"
                }
            ],
            "translations": {
                "en": {
                    "name": "News",
                    "description": "An RSS/Atom feed reader"
                }
            },
            "recommendations": 0,
            "featured": false
        }
    ]


translations
    Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.

nightly
    True if the release is a nightly version. Currently we only support one nightly release because downgrading apps is unsupported. New nightly releases are not required to have a higher version than the previous one. Instead look at the **lastModified** attribute to detect updates.

screenshots
    Guaranteed to be HTTPS

download
    Download archive location, guaranteed to be HTTPS

versionSpec
    Required versions (minimum and maximum versions) are transformed to semantic version specs. If a field is a \*, this means that there is no version requirement. The following permutations can occur:

     * **All versions**: \*
     * **Maximum version only**: <8.1.2
     * **Minimum version only**: >=9.3.2
     * **Maximum and minimum version**: >=9.3.2 <8.1.2

checksum
    The checksum is generated by running sha256sum over the downloaded archive.

recommendations
    How many users recommend the app

featured
    Simple boolean flag which will be presented to the user as "hey take a look at this app". Does not imply that it has been reviewed or we recommend it officially

categories
    The string value is the category's id attribute, see :ref:`api-all-categories`

.. _api-all-categories:

Get All Categories
~~~~~~~~~~~~~~~~~~
This route will return all categories and their translations.

* **Url**: GET /api/v1/categories.json

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl http://localhost:8000/api/v1/categories.json -H 'If-None-Match: "4-2016-06-11 10:37:24+00:00"'

* **Returns**: application/json

.. code-block:: json

    [
        {
            "id": "games",
            "translations": {
                "en": {
                    "name": "Games",
                    "description": ""
                },
                "de": {
                    "name": "Spiele",
                    "description": ""
                },
                "fr": {
                    "name": "Jeux",
                    "description": ""
                }
            }
        },
        {
            "id": "multimedia",
            "translations": {
                "en": {
                    "name": "Multimedia",
                    "description": ""
                },
                "de": {
                    "name": "Multimedia",
                    "description": ""
                },
                "fr": {
                    "name": "Multimedia",
                    "description": ""
                }
            }
        },
        {
            "id": "pim",
            "translations": {
                "en": {
                    "name": "PIM",
                    "description": ""
                },
                "de": {
                    "name": "PIM",
                    "description": ""
                },
                "fr": {
                    "name": "PIM",
                    "description": ""
                }
            }
        },
        {
            "id": "tools",
            "translations": {
                "en": {
                    "name": "Tools",
                    "description": ""
                },
                "de": {
                    "name": "Werkzeuge",
                    "description": ""
                },
                "fr": {
                    "name": "Outil",
                    "description": ""
                }
            }
        }
    ]


translations
    Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.



.. _api-delete-app:

Delete an App
~~~~~~~~~~~~~
Only app owners are allowed to delete an app. The owner is the user that pushes the first release of an app to the store.

Deleting an app will also delete all releases which are associated with it.

* **Url**: DELETE /api/v1/apps/{**app-id**}

* **Url parameters**:

 * **app-id**: app id, lower case ASCII characters and underscores are allowed

* **Authentication**: Basic, Token

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
 * **app-version**: app version, semantic version, digits only or digits-nightly for deleting a nightly (e.g. 7.9.1-nightly)

* **Authentication**: Basic, Token

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

* **Authentication** Basic, Token

* **Content-Type**: application/json

* **Request body**:

  * **download**: An Https (Http is not allowed!) link to the archive packaged (maximum size: 20 Megabytes) as tar.gz, info.xml must be smaller than 512Kb
  * **nightly (Optional)**: If true this release will be stored as a nightly. All previous nightly releases will be deleted.
  * **checksum (Optional)**: If not given we will calculate the sha256sum on the downloaded archive. If you are paranoid or host your packages on a host that you don't trust, you can supply your own sha256sum which can be generated by running::

      sha256sum release.tar.gz

  .. code-block:: json

      {
          "download": "https://example.com/release.tar.gz",
          "checksum": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15",
          "nightly": false
      }


* **Example CURL request**::

        curl -X POST -u "user:password" http://localhost:8000/api/v1/apps/releases -H "Content-Type: application/json" -d '{"download":"https://example.com/release.tar.gz"}'

* **Returns**:

  * **HTTP 200**: If the app release was update successfully
  * **HTTP 201**: If the app release was created successfully
  * **HTTP 400**: If the app contains invalid data, is too large or could not be downloaded
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to create or update the app release

If there is no app with the given app id yet, a new app is created and the owner is set in to the logged in user. Then the **info.xml** file which lies in the compressed archive's folder **app-id/appinfo/info.xml** is being parsed and validated. The validated result is then saved in the database. Both owners and co-maintainers are allowed to upload new releases.

The following character maximum lengths are enforced:

* All description Strings are (almost) of unlimited size
* All Url Strings have a maximum of 256 characters
* All other Strings have a maximum of 128 characters

A minimum valid **info.xml** would look like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">
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
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">
        <id>news</id>

        <!-- translation can be done via the lang attribute, defaults to English -->
        <name lang="de">Nachrichten</name>
        <name>News</name>

        <!-- description tag allows Markdown -->
        <description lang="en">An RSS/Atom feed reader</description>
        <description lang="de"><![CDATA[Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann]]></description>

        <!-- semantic version, three digits separated by a dot -->
        <version>8.8.2</version>

        <!-- only agpl is an acceptable license -->
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



