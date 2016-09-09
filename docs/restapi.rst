REST API
========

A REST API for publishing and deleting app releases has been built into the store from day one to help release automation.

All APIs can easily be used with :doc:`ncdev <ncdev>`

Authentication
--------------

Several routes require authentication. The following authentication methods are supported:

* **Basic**: Http header where **CREDENTIALS** is ``base64encode('user:password')``::

    Authorization: Basic CREDENTIALS

* **Token**: Http header where **TOKEN** is a token which can be looked up in your account settings or `acquired through the API <api-token_>`_::

    Authorization: Token TOKEN

Specification
-------------

The following API routes are present:

* :ref:`api-token`

* :ref:`api-token-new`

* :ref:`api-all-categories`

* :ref:`api-all-releases`

* :ref:`api-create-release`

* :ref:`api-delete-release`

* :ref:`api-delete-app`

* :ref:`api-all-app-ratings`

.. _api-token:

Get API Token
~~~~~~~~~~~~~
This route will return the API token for the authenticated user. If no token
exists, one will be generated.

* **Url**: POST /api/v1/token

* **Authentication**: Basic, Session

* **Example CURL request**::

    curl -X POST https://apps.nextcloud.com/api/v1/token -u "user:password"

* **Returns**: application/json

.. code-block:: json

    {"token":"4b92477ff8d5fe889be75db4c7d9a09116276920"}

.. _api-token-new:

Regenerate API Token
~~~~~~~~~~~~~~~~~~~~
This route will generate and return a new API token for the authenticated user
regardless of whether a token already exists.

* **Url**: POST /api/v1/token/new

* **Authentication**: Basic, Token

* **Example CURL request**::

    curl -X POST https://apps.nextcloud.com/api/v1/token/new -u "user:password"

* **Returns**: application/json

.. code-block:: json

    {"token":"ca3fb97920705d2c2ecdb0900f8ed5cf5744704d"}


.. _api-all-categories:

Get All Categories
~~~~~~~~~~~~~~~~~~
This route will return all categories and their translations.

* **Url**: GET /api/v1/categories.json

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl https://apps.nextcloud.com/api/v1/categories.json -H 'If-None-Match: "4-2016-06-11 10:37:24+00:00"'

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

    curl https://apps.nextcloud.com/api/v1/platform/9.0.0/apps.json -H 'If-None-Match: "1-1-2016-06-17 23:08:58.042321+00:00"'

* **Returns**: application/json

.. code-block:: json

    [
        {
            "id": "news",
            "categories": [
                "multimedia"
            ],
            "authors": [
                {
                    "name": "Bernhard Posselt",
                    "mail": "",
                    "homepage": ""
                },
                {
                    "name": "Alessandro Cosentino",
                    "mail": "",
                    "homepage": ""
                },
                {
                    "name": "Jan-Christoph Borchardt",
                    "mail": "",
                    "homepage": ""
                }
            ],
            "userDocs": "https://github.com/owncloud/news/wiki#user-documentation",
            "adminDocs": "https://github.com/owncloud/news#readme",
            "developerDocs": "https://github.com/owncloud/news/wiki#developer-documentation",
            "issueTracker": "https://github.com/owncloud/news/issues",
            "website": "https://github.com/owncloud/news",
            "created": "2016-06-25T16:08:56.794719Z",
            "lastModified": "2016-06-25T16:49:25.326855Z",
            "ratingOverall": 0.5,
            "ratingRecent": 1.0,
            "releases": [
                {
                    "version": "9.0.4",
                    "phpExtensions": [
                        {
                            "id": "libxml",
                            "versionSpec": ">=2.7.8",
                            "rawVersionSpec": ">=2.7.8"
                        },
                        {
                            "id": "curl",
                            "versionSpec": "*",
                            "rawVersionSpec": "*"
                        },
                        {
                            "id": "SimpleXML",
                            "versionSpec": "*",
                            "rawVersionSpec": "*"
                        },
                        {
                            "id": "iconv",
                            "versionSpec": "*",
                            "rawVersionSpec": "*"
                        }
                    ],
                    "databases": [
                        {
                            "id": "pgsql",
                            "versionSpec": ">=9.4.0",
                            "rawVersionSpec": ">=9.4"
                        },
                        {
                            "id": "sqlite",
                            "versionSpec": "*",
                            "rawVersionSpec": "*"
                        },
                        {
                            "id": "mysql",
                            "versionSpec": ">=5.5.0",
                            "rawVersionSpec": ">=5.5"
                        }
                    ],
                    "shellCommands": [
                        "grep"
                    ],
                    "phpVersionSpec": ">=5.6.0",
                    "platformVersionSpec": ">=9.0.0 <9.2.0",
                    "rawPhpVersionSpec": ">=5.6",
                    "rawPlatformVersionSpec": ">=10 <=10"
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
                    "summary": "An RSS/Atom feed reader",
                    "description": "# This is markdown\nnext line"
                }
            },
            "featured": false,
            "certificate": "-----BEGIN CERTIFICATE-----\r\nMIIEojCCA4qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwezELMAkGA1UEBhMCREUx\r\nGzAZBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzEXMBUGA1UECgwOTmV4dGNsb3Vk\r\nIEdtYkgxNjA0BgNVBAMMLU5leHRjbG91ZCBDb2RlIFNpZ25pbmcgSW50ZXJtZWRp\r\nYXRlIEF1dGhvcml0eTAeFw0xNjA2MTIyMTA1MDZaFw00MTA2MDYyMTA1MDZaMGYx\r\nCzAJBgNVBAYTAkRFMRswGQYDVQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxEjAQBgNV\r\nBAcMCVN0dXR0Z2FydDEXMBUGA1UECgwOTmV4dGNsb3VkIEdtYkgxDTALBgNVBAMM\r\nBGNvcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUxcrn2DC892IX\r\n8+dJjZVh9YeHF65n2ha886oeAizOuHBdWBfzqt+GoUYTOjqZF93HZMcwy0P+xyCf\r\nQqak5Ke9dybN06RXUuGP45k9UYBp03qzlUzCDalrkj+Jd30LqcSC1sjRTsfuhc+u\r\nvH1IBuBnf7SMUJUcoEffbmmpAPlEcLHxlUGlGnz0q1e8UFzjbEFj3JucMO4ys35F\r\nqZS4dhvCngQhRW3DaMlQLXEUL9k3kFV+BzlkPzVZEtSmk4HJujFCnZj1vMcjQBg\/\r\nBqq1HCmUB6tulnGcxUzt\/Z\/oSIgnuGyENeke077W3EyryINL7EIyD4Xp7sxLizTM\r\nFCFCjjH1AgMBAAGjggFDMIIBPzAJBgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIG\r\nQDAzBglghkgBhvhCAQ0EJhYkT3BlblNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRp\r\nZmljYXRlMB0GA1UdDgQWBBQwc1H9AL8pRlW2e5SLCfPPqtqc0DCBpQYDVR0jBIGd\r\nMIGagBRt6m6qqTcsPIktFz79Ru7DnnjtdKF+pHwwejELMAkGA1UEBhMCREUxGzAZ\r\nBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzESMBAGA1UEBwwJU3R1dHRnYXJ0MRcw\r\nFQYDVQQKDA5OZXh0Y2xvdWQgR21iSDEhMB8GA1UEAwwYTmV4dGNsb3VkIFJvb3Qg\r\nQXV0aG9yaXR5ggIQADAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUH\r\nAwEwDQYJKoZIhvcNAQELBQADggEBADZ6+HV\/+0NEH3nahTBFxO6nKyR\/VWigACH0\r\nnaV0ecTcoQwDjKDNNFr+4S1WlHdwITlnNabC7v9rZ\/6QvbkrOTuO9fOR6azp1EwW\r\n2pixWqj0Sb9\/dSIVRpSq+jpBE6JAiX44dSR7zoBxRB8DgVO2Afy0s80xEpr5JAzb\r\nNYuPS7M5UHdAv2dr16fDcDIvn+vk92KpNh1NTeZFjBbRVQ9DXrgkRGW34TK8uSLI\r\nYG6jnfJ6eJgTaO431ywWPXNg1mUMaT\/+QBOgB299QVCKQU+lcZWptQt+RdsJUm46\r\nNY\/nARy4Oi4uOe88SuWITj9KhrFmEvrUlgM8FvoXA1ldrR7KiEg=\r\n-----END CERTIFICATE-----"
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

rawVersionSpec
    Non semantic versions as they occur in the info.xml. The following permutations can occur:

     * **All versions**: \*
     * **Maximum version only**: <=8.1.2
     * **Minimum version only**: >=9.3.2
     * **Maximum and minimum version**: >=9.3.2 <=8.1.2


ratingRecent
    Rating from 0.0 to 1.0 (0.0 being the worst, 1.0 being the best) in the past 90 days

ratingOverall
    Rating from 0.0 to 1.0 (0.0 being the worst, 1.0 being the best) of all time

checksum
    The checksum is generated by running sha256sum over the downloaded archive.

description
    A full blown description containing markdown

summary
    A brief explanation what the app tries to do

featured
    Simple boolean flag which will be presented to the user as "hey take a look at this app". Does not imply that it has been reviewed or we recommend it officially

categories
    The string value is the category's id attribute, see :ref:`api-all-categories`

.. _api-create-release:

Publish a New App Release
~~~~~~~~~~~~~~~~~~~~~~~~~
The following request will create a new app release or update an existing release:

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

        curl -X POST -u "user:password" https://apps.nextcloud.com/api/v1/apps/releases -H "Content-Type: application/json" -d '{"download":"https://example.com/release.tar.gz"}'

* **Returns**:

  * **HTTP 200**: If the app release was update successfully
  * **HTTP 201**: If the app release was created successfully
  * **HTTP 400**: If the app contains invalid data, is too large or could not be downloaded
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to create or update the app release

If there is no app with the given app id yet, a new app is created and the owner is set in to the logged in user. Then the **info.xml** file which lies in the compressed archive's folder **app-id/appinfo/info.xml** is being parsed and validated. The validated result is then saved in the database. Both owners and co-maintainers are allowed to upload new releases.

If the app release version is the latest version, everything is updated. If it's not the latest release, only release relevant details are updated. This **excludes** the following info.xml elements:

  * name
  * summary
  * description
  * category
  * author
  * documentation
  * bugs
  * website
  * discussion
  * screenshot


For more information about validation and which **info.xml** fields are parsed, see :ref:`app-metadata`

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

    curl -X DELETE https://apps.nextcloud.com/api/v1/apps/news/releases/9.0.0 -u "user:password"


* **Returns**:

  * **HTTP 204**: If the app release was deleted successfully
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app release
  * **HTTP 404**: If the app release could not be found

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

    curl -X DELETE https://apps.nextcloud.com/api/v1/apps/news -u "user:password"


* **Returns**:

 * **HTTP 204**: If the app was deleted successfully
 * **HTTP 401**: If the user is not authenticated
 * **HTTP 403**: If the user is not authorized to delete the app
 * **HTTP 404**: If the app could not be found

.. _api-all-app-ratings:

Get All App Ratings
~~~~~~~~~~~~~~~~~~~
This route will return all rating comments.

* **Url**: GET /api/v1/apps/ratings.json

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl https://apps.nextcloud.com/api/v1/apps/ratings.json -H 'If-None-Match: ""1-2016-09-03 17:11:38.772856+00:00""'

* **Returns**: application/json

.. code-block:: json

    [
        {
            "rating": 1.0,
            "ratedAt": "2016-09-03T17:11:38.772856Z",
            "translations": {
                "en": {
                    "comment": "I like it"
                }
            },
            "user": {
                "id": 1,
                "firstName": "Tom",
                "lastName": "Jones"
            },
            "app": "keeweb"
        }
    ]


translations
    can contain 0 or any number of translated comments. If no comment is available for the currently chosen language, only the rating should be considered. Contains Markdown.
rating
    range from 0.0 (worst) to 1.0 (best)
