Store REST API
==============

A REST API for publishing and deleting app releases has been built into the store from day one to help release automation.

API Stability Contract
----------------------
The API level **will change** if the following occurs:

* a required HTTP request header is added
* a required request parameter is added
* a JSON field of a response object is removed
* a JSON field of a response object is changed to appear optionally
* a JSON field of a response object is changed to a different datatype
* an explicitly documented HTTP response header is removed
* an explicitly documented HTTP response header is changed to a different datatype
* the meaning of an API call changes

The API level **will not change** if:

* a new HTTP response header is added
* an optional new HTTP request header is added
* a new response parameter is added
* the order of the JSON attributes is changed
* if app validation after uploading an app release is changed in any way

You have to design your app with these things in mind:

* Don't depend on the order of object attributes. In JSON it does not matter where the object attribute is since you access the value by name, not by index
* Don't limit your app to the currently available attributes. New ones might be added. If you don't handle them, ignore them
* Use a library to compare versions, ideally one that uses semantic versioning

Authentication
--------------

Several routes require authentication. The following authentication methods are supported:

* **Basic**: Http header where **CREDENTIALS** is ``base64encode('user:password')``::

    Authorization: Basic CREDENTIALS

* **Token**: Http header where **TOKEN** is a token which can be looked up in your account settings or `acquired through the API <api-token_>`_::

    Authorization: Token TOKEN

.. note:: If you created your account using GitHub you will always need to use token authentication since we do not have access to your password. The token can be looked up in `your account settings <https://apps.nextcloud.com/account/token>`_

Specification
-------------

The following API routes are present:

* :ref:`api-token`

* :ref:`api-token-new`

* :ref:`api-all-categories`

* :ref:`api-all-platforms`

* :ref:`api-all-compatible-releases`

* :ref:`api-all-releases`

* :ref:`api-register-app`

* :ref:`api-create-release`

* :ref:`api-delete-release`

* :ref:`api-delete-nightly-release`

* :ref:`api-delete-app`

* :ref:`api-all-app-ratings`

* :ref:`api-get-app-discover`

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


.. _api-all-platforms:

Get All Nextcloud Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~
This will return all the Nextcloud releases that the store knows about. To check if a release can actually be downloaded check the **hasRelease** flag.

.. note:: Unsupported Nextcloud releases will be removed from the response

.. note:: To find the latest version that has a release you will need to use a semantic version library to sort the list. The result is unsorted.

* **Url**: GET /api/v1/platforms.json

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl https://apps.nextcloud.com/api/v1/platforms.json -H 'If-None-Match: "4-2016-06-11 10:37:24+00:00"'

* **Returns**: application/json

.. code-block:: json

    [
        {
            "hasRelease": false,
            "version": "99.0.0",
            "isSupported": true
        },
        {
            "hasRelease": true,
            "version": "9.0.0",
            "isSupported": false
        }
    ]

hasRelease
    boolean flag that indicates if the Nextcloud release is officially out yet
isSupported
    boolean flag that indicates if the Nextcloud is officially supported

.. _api-all-compatible-releases:

Get All Apps and Releases Compatible with a Nextcloud Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This route will return all releases to display inside Nextcloud's apps admin area filtered by the releases which are marked as compatible with the platforms version.

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
            "discussion": "https://help.nextcloud.com/c/apps/news",
            "created": "2016-06-25T16:08:56.794719Z",
            "lastModified": "2016-06-25T16:49:25.326855Z",
            "ratingOverall": 0.5,
            "ratingNumOverall": 20,
            "ratingRecent": 1.0,
            "ratingNumRecent": 10,
            "releases": [
                {
                    "version": "9.0.4-alpha.1",
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
                    "rawPlatformVersionSpec": ">=10 <=10",
                    "minIntSize": 64,
                    "isNightly": false,
                    "download": "https://github.com/owncloud/news/releases/download/8.8.0/news.tar.gz",
                    "created": "2016-06-25T16:08:56.796646Z",
                    "licenses": [
                        "agpl"
                    ],
                    "lastModified": "2016-06-25T16:49:25.319425Z",
                    "signature": "909377e1a695bbaa415c10ae087ae1cc48e88066d20a5a7a8beed149e9fad3d5",
                    "translations": {
                        "en": {
                            "changelog": "* **Bugfix**: Pad API last modified timestamp to milliseconds in updated items API to return only new items. API users however need to re-sync their complete contents, #24\n* **Bugfix**: Do not pad milliseconds for non millisecond timestamps in API"
                        }
                    }
                }
            ],
            "screenshots": [
                {
                    "url": "https://example.com/news.jpg",
                    "smallThumbnail": ""
                }
            ],
            "translations": {
                "en": {
                    "name": "News",
                    "summary": "An RSS/Atom feed reader",
                    "description": "# This is markdown\nnext line"
                }
            },
            "isFeatured": false,
            "certificate": "-----BEGIN CERTIFICATE-----\r\nMIIEojCCA4qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwezELMAkGA1UEBhMCREUx\r\nGzAZBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzEXMBUGA1UECgwOTmV4dGNsb3Vk\r\nIEdtYkgxNjA0BgNVBAMMLU5leHRjbG91ZCBDb2RlIFNpZ25pbmcgSW50ZXJtZWRp\r\nYXRlIEF1dGhvcml0eTAeFw0xNjA2MTIyMTA1MDZaFw00MTA2MDYyMTA1MDZaMGYx\r\nCzAJBgNVBAYTAkRFMRswGQYDVQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxEjAQBgNV\r\nBAcMCVN0dXR0Z2FydDEXMBUGA1UECgwOTmV4dGNsb3VkIEdtYkgxDTALBgNVBAMM\r\nBGNvcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUxcrn2DC892IX\r\n8+dJjZVh9YeHF65n2ha886oeAizOuHBdWBfzqt+GoUYTOjqZF93HZMcwy0P+xyCf\r\nQqak5Ke9dybN06RXUuGP45k9UYBp03qzlUzCDalrkj+Jd30LqcSC1sjRTsfuhc+u\r\nvH1IBuBnf7SMUJUcoEffbmmpAPlEcLHxlUGlGnz0q1e8UFzjbEFj3JucMO4ys35F\r\nqZS4dhvCngQhRW3DaMlQLXEUL9k3kFV+BzlkPzVZEtSmk4HJujFCnZj1vMcjQBg\/\r\nBqq1HCmUB6tulnGcxUzt\/Z\/oSIgnuGyENeke077W3EyryINL7EIyD4Xp7sxLizTM\r\nFCFCjjH1AgMBAAGjggFDMIIBPzAJBgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIG\r\nQDAzBglghkgBhvhCAQ0EJhYkT3BlblNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRp\r\nZmljYXRlMB0GA1UdDgQWBBQwc1H9AL8pRlW2e5SLCfPPqtqc0DCBpQYDVR0jBIGd\r\nMIGagBRt6m6qqTcsPIktFz79Ru7DnnjtdKF+pHwwejELMAkGA1UEBhMCREUxGzAZ\r\nBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzESMBAGA1UEBwwJU3R1dHRnYXJ0MRcw\r\nFQYDVQQKDA5OZXh0Y2xvdWQgR21iSDEhMB8GA1UEAwwYTmV4dGNsb3VkIFJvb3Qg\r\nQXV0aG9yaXR5ggIQADAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUH\r\nAwEwDQYJKoZIhvcNAQELBQADggEBADZ6+HV\/+0NEH3nahTBFxO6nKyR\/VWigACH0\r\nnaV0ecTcoQwDjKDNNFr+4S1WlHdwITlnNabC7v9rZ\/6QvbkrOTuO9fOR6azp1EwW\r\n2pixWqj0Sb9\/dSIVRpSq+jpBE6JAiX44dSR7zoBxRB8DgVO2Afy0s80xEpr5JAzb\r\nNYuPS7M5UHdAv2dr16fDcDIvn+vk92KpNh1NTeZFjBbRVQ9DXrgkRGW34TK8uSLI\r\nYG6jnfJ6eJgTaO431ywWPXNg1mUMaT\/+QBOgB299QVCKQU+lcZWptQt+RdsJUm46\r\nNY\/nARy4Oi4uOe88SuWITj9KhrFmEvrUlgM8FvoXA1ldrR7KiEg=\r\n-----END CERTIFICATE-----",
            "signatureDigest": "sha512"
        }
    ]


translations
    Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.

isNightly
    True if the release is a nightly version. New nightly releases are not required to have a higher version than the previous one to be considered greater. Instead look at the **lastModified** attribute to detect updates if both nightly versions are equal. Example: 1.0.0 is equal to 1.0.0, however if the second one has a nightly flag, then the second one is greater. If both versions have nightly flags and are equal, the **lastModified** is used to determine the precedence.

screenshots
    Guaranteed to be HTTPS

smallThumbnail
    Small thumbnail which can be used as preview image. Guaranteed to be HTTPS. Not required, so if not present or an empty string, use the screenshot url instead.

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

ratingNumRecent
    Number of ratings for an app in the past 90 days, as in: how many votes were casted. 0 Means no ratings yet.

ratingOverall
    Rating from 0.0 to 1.0 (0.0 being the worst, 1.0 being the best) of all time

ratingNumOverall
    Number of ratings for an app overall, as in: how many votes were casted. 0 Means no ratings yet.

signature
    A signature using SHA512 and the app's certificate

signatureDigest
    The hashing algorithm that is used to verify the signature

description
    A full blown description containing Markdown

summary
    A brief explanation what the app tries to do

isFeatured
    Simple boolean flag which will be presented to the user as "hey take a look at this app". Does not imply that it has been reviewed or we recommend it officially

categories
    The string value is the category's id attribute, see :ref:`api-all-categories`

changelog
    The translated release changelog in Markdown. Can be empty for all languages

version
    A semantic version without build metadata (e.g. 1.3.0, 1.2.1-alpha.1)



.. _api-all-releases:

Get All Apps and Releases
~~~~~~~~~~~~~~~~~~~~~~~~~
This route will return all releases to display inside Nextcloud's apps admin area.

* **Url**: GET /api/v1/apps.json
* **Url parameters**: None

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl https://apps.nextcloud.com/api/v1/apps.json -H 'If-None-Match: "1-1-2016-06-17 23:08:58.042321+00:00"'

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
            "discussion": "https://help.nextcloud.com/c/apps/news",
            "created": "2016-06-25T16:08:56.794719Z",
            "lastModified": "2016-06-25T16:49:25.326855Z",
            "ratingOverall": 0.5,
            "ratingNumOverall": 20,
            "ratingRecent": 1.0,
            "ratingNumRecent": 10,
            "releases": [
                {
                    "version": "9.0.4-alpha.1",
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
                    "rawPlatformVersionSpec": ">=10 <=10",
                    "minIntSize": 64,
                    "isNightly": false,
                    "download": "https://github.com/owncloud/news/releases/download/8.8.0/news.tar.gz",
                    "created": "2016-06-25T16:08:56.796646Z",
                    "licenses": [
                        "agpl"
                    ],
                    "lastModified": "2016-06-25T16:49:25.319425Z",
                    "signature": "909377e1a695bbaa415c10ae087ae1cc48e88066d20a5a7a8beed149e9fad3d5",
                    "translations": {
                        "en": {
                            "changelog": "* **Bugfix**: Pad API last modified timestamp to milliseconds in updated items API to return only new items. API users however need to re-sync their complete contents, #24\n* **Bugfix**: Do not pad milliseconds for non millisecond timestamps in API"
                        }
                    }
                }
            ],
            "screenshots": [
                {
                    "url": "https://example.com/news.jpg",
                    "smallThumbnail": ""
                }
            ],
            "translations": {
                "en": {
                    "name": "News",
                    "summary": "An RSS/Atom feed reader",
                    "description": "# This is markdown\nnext line"
                }
            },
            "isFeatured": false,
            "certificate": "-----BEGIN CERTIFICATE-----\r\nMIIEojCCA4qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwezELMAkGA1UEBhMCREUx\r\nGzAZBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzEXMBUGA1UECgwOTmV4dGNsb3Vk\r\nIEdtYkgxNjA0BgNVBAMMLU5leHRjbG91ZCBDb2RlIFNpZ25pbmcgSW50ZXJtZWRp\r\nYXRlIEF1dGhvcml0eTAeFw0xNjA2MTIyMTA1MDZaFw00MTA2MDYyMTA1MDZaMGYx\r\nCzAJBgNVBAYTAkRFMRswGQYDVQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxEjAQBgNV\r\nBAcMCVN0dXR0Z2FydDEXMBUGA1UECgwOTmV4dGNsb3VkIEdtYkgxDTALBgNVBAMM\r\nBGNvcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUxcrn2DC892IX\r\n8+dJjZVh9YeHF65n2ha886oeAizOuHBdWBfzqt+GoUYTOjqZF93HZMcwy0P+xyCf\r\nQqak5Ke9dybN06RXUuGP45k9UYBp03qzlUzCDalrkj+Jd30LqcSC1sjRTsfuhc+u\r\nvH1IBuBnf7SMUJUcoEffbmmpAPlEcLHxlUGlGnz0q1e8UFzjbEFj3JucMO4ys35F\r\nqZS4dhvCngQhRW3DaMlQLXEUL9k3kFV+BzlkPzVZEtSmk4HJujFCnZj1vMcjQBg\/\r\nBqq1HCmUB6tulnGcxUzt\/Z\/oSIgnuGyENeke077W3EyryINL7EIyD4Xp7sxLizTM\r\nFCFCjjH1AgMBAAGjggFDMIIBPzAJBgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIG\r\nQDAzBglghkgBhvhCAQ0EJhYkT3BlblNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRp\r\nZmljYXRlMB0GA1UdDgQWBBQwc1H9AL8pRlW2e5SLCfPPqtqc0DCBpQYDVR0jBIGd\r\nMIGagBRt6m6qqTcsPIktFz79Ru7DnnjtdKF+pHwwejELMAkGA1UEBhMCREUxGzAZ\r\nBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzESMBAGA1UEBwwJU3R1dHRnYXJ0MRcw\r\nFQYDVQQKDA5OZXh0Y2xvdWQgR21iSDEhMB8GA1UEAwwYTmV4dGNsb3VkIFJvb3Qg\r\nQXV0aG9yaXR5ggIQADAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUH\r\nAwEwDQYJKoZIhvcNAQELBQADggEBADZ6+HV\/+0NEH3nahTBFxO6nKyR\/VWigACH0\r\nnaV0ecTcoQwDjKDNNFr+4S1WlHdwITlnNabC7v9rZ\/6QvbkrOTuO9fOR6azp1EwW\r\n2pixWqj0Sb9\/dSIVRpSq+jpBE6JAiX44dSR7zoBxRB8DgVO2Afy0s80xEpr5JAzb\r\nNYuPS7M5UHdAv2dr16fDcDIvn+vk92KpNh1NTeZFjBbRVQ9DXrgkRGW34TK8uSLI\r\nYG6jnfJ6eJgTaO431ywWPXNg1mUMaT\/+QBOgB299QVCKQU+lcZWptQt+RdsJUm46\r\nNY\/nARy4Oi4uOe88SuWITj9KhrFmEvrUlgM8FvoXA1ldrR7KiEg=\r\n-----END CERTIFICATE-----",
            "signatureDigest": "sha512"
        }
    ]


translations
    Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.

isNightly
    True if the release is a nightly version. New nightly releases are not required to have a higher version than the previous one to be considered greater. Instead look at the **lastModified** attribute to detect updates if both nightly versions are equal. Example: 1.0.0 is equal to 1.0.0, however if the second one has a nightly flag, then the second one is greater. If both versions have nightly flags and are equal, the **lastModified** is used to determine the precedence.

screenshots
    Guaranteed to be HTTPS

smallThumbnail
    Small thumbnail which can be used as preview image. Guaranteed to be HTTPS. Not required, so if not present or an empty string, use the screenshot url instead.

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

ratingNumRecent
    Number of ratings for an app in the past 90 days, as in: how many votes were casted. 0 Means no ratings yet.

ratingOverall
    Rating from 0.0 to 1.0 (0.0 being the worst, 1.0 being the best) of all time

ratingNumOverall
    Number of ratings for an app overall, as in: how many votes were casted. 0 Means no ratings yet.

signature
    A signature using SHA512 and the app's certificate

signatureDigest
    The hashing algorithm that is used to verify the signature

description
    A full blown description containing Markdown

summary
    A brief explanation what the app tries to do

isFeatured
    Simple boolean flag which will be presented to the user as "hey take a look at this app". Does not imply that it has been reviewed or we recommend it officially

categories
    The string value is the category's id attribute, see :ref:`api-all-categories`

changelog
    The translated release changelog in Markdown. Can be empty for all languages

version
    A semantic version without build metadata (e.g. 1.3.0, 1.2.1-alpha.1)



.. _api-register-app:

Register a New App
~~~~~~~~~~~~~~~~~~
Before you can upload release you first need to register its app id. To do that use:

* **Url**: POST /api/v1/apps

* **Authentication** Basic, Token

* **Content-Type**: application/json

* **Request body**:

  * **certificate**: Your public certificate whose CN is equal to the app id, should be stored in **~/.nextcloud/certificates/APP_ID.cert** where **APP_ID** is your app's id
  * **signature**: A SHA512 signature over the app id using the app's certificate, can be created using::

        echo -n "APP_ID" | openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key | openssl base64

  .. code-block:: json

      {
          "certificate": "certificate": "-----BEGIN CERTIFICATE-----\r\nMIIEojCCA4qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwezELMAkGA1UEBhMCREUx\r\nGzAZBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzEXMBUGA1UECgwOTmV4dGNsb3Vk\r\nIEdtYkgxNjA0BgNVBAMMLU5leHRjbG91ZCBDb2RlIFNpZ25pbmcgSW50ZXJtZWRp\r\nYXRlIEF1dGhvcml0eTAeFw0xNjA2MTIyMTA1MDZaFw00MTA2MDYyMTA1MDZaMGYx\r\nCzAJBgNVBAYTAkRFMRswGQYDVQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxEjAQBgNV\r\nBAcMCVN0dXR0Z2FydDEXMBUGA1UECgwOTmV4dGNsb3VkIEdtYkgxDTALBgNVBAMM\r\nBGNvcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUxcrn2DC892IX\r\n8+dJjZVh9YeHF65n2ha886oeAizOuHBdWBfzqt+GoUYTOjqZF93HZMcwy0P+xyCf\r\nQqak5Ke9dybN06RXUuGP45k9UYBp03qzlUzCDalrkj+Jd30LqcSC1sjRTsfuhc+u\r\nvH1IBuBnf7SMUJUcoEffbmmpAPlEcLHxlUGlGnz0q1e8UFzjbEFj3JucMO4ys35F\r\nqZS4dhvCngQhRW3DaMlQLXEUL9k3kFV+BzlkPzVZEtSmk4HJujFCnZj1vMcjQBg\/\r\nBqq1HCmUB6tulnGcxUzt\/Z\/oSIgnuGyENeke077W3EyryINL7EIyD4Xp7sxLizTM\r\nFCFCjjH1AgMBAAGjggFDMIIBPzAJBgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIG\r\nQDAzBglghkgBhvhCAQ0EJhYkT3BlblNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRp\r\nZmljYXRlMB0GA1UdDgQWBBQwc1H9AL8pRlW2e5SLCfPPqtqc0DCBpQYDVR0jBIGd\r\nMIGagBRt6m6qqTcsPIktFz79Ru7DnnjtdKF+pHwwejELMAkGA1UEBhMCREUxGzAZ\r\nBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzESMBAGA1UEBwwJU3R1dHRnYXJ0MRcw\r\nFQYDVQQKDA5OZXh0Y2xvdWQgR21iSDEhMB8GA1UEAwwYTmV4dGNsb3VkIFJvb3Qg\r\nQXV0aG9yaXR5ggIQADAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUH\r\nAwEwDQYJKoZIhvcNAQELBQADggEBADZ6+HV\/+0NEH3nahTBFxO6nKyR\/VWigACH0\r\nnaV0ecTcoQwDjKDNNFr+4S1WlHdwITlnNabC7v9rZ\/6QvbkrOTuO9fOR6azp1EwW\r\n2pixWqj0Sb9\/dSIVRpSq+jpBE6JAiX44dSR7zoBxRB8DgVO2Afy0s80xEpr5JAzb\r\nNYuPS7M5UHdAv2dr16fDcDIvn+vk92KpNh1NTeZFjBbRVQ9DXrgkRGW34TK8uSLI\r\nYG6jnfJ6eJgTaO431ywWPXNg1mUMaT\/+QBOgB299QVCKQU+lcZWptQt+RdsJUm46\r\nNY\/nARy4Oi4uOe88SuWITj9KhrFmEvrUlgM8FvoXA1ldrR7KiEg=\r\n-----END CERTIFICATE-----",
          "signature": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15"
      }


* **Example CURL request**::

        curl -X POST -u "user:password" https://apps.nextcloud.com/api/v1/apps -H "Content-Type: application/json" -d '{"certificate": "certificate": "-----BEGIN CERTIFICATE-----\r\nMIIEojCCA4qgAwIBAgICEAAwDQYJKoZIhvcNAQELBQAwezELMAkGA1UEBhMCREUx\r\nGzAZBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzEXMBUGA1UECgwOTmV4dGNsb3Vk\r\nIEdtYkgxNjA0BgNVBAMMLU5leHRjbG91ZCBDb2RlIFNpZ25pbmcgSW50ZXJtZWRp\r\nYXRlIEF1dGhvcml0eTAeFw0xNjA2MTIyMTA1MDZaFw00MTA2MDYyMTA1MDZaMGYx\r\nCzAJBgNVBAYTAkRFMRswGQYDVQQIDBJCYWRlbi1XdWVydHRlbWJlcmcxEjAQBgNV\r\nBAcMCVN0dXR0Z2FydDEXMBUGA1UECgwOTmV4dGNsb3VkIEdtYkgxDTALBgNVBAMM\r\nBGNvcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUxcrn2DC892IX\r\n8+dJjZVh9YeHF65n2ha886oeAizOuHBdWBfzqt+GoUYTOjqZF93HZMcwy0P+xyCf\r\nQqak5Ke9dybN06RXUuGP45k9UYBp03qzlUzCDalrkj+Jd30LqcSC1sjRTsfuhc+u\r\nvH1IBuBnf7SMUJUcoEffbmmpAPlEcLHxlUGlGnz0q1e8UFzjbEFj3JucMO4ys35F\r\nqZS4dhvCngQhRW3DaMlQLXEUL9k3kFV+BzlkPzVZEtSmk4HJujFCnZj1vMcjQBg\/\r\nBqq1HCmUB6tulnGcxUzt\/Z\/oSIgnuGyENeke077W3EyryINL7EIyD4Xp7sxLizTM\r\nFCFCjjH1AgMBAAGjggFDMIIBPzAJBgNVHRMEAjAAMBEGCWCGSAGG+EIBAQQEAwIG\r\nQDAzBglghkgBhvhCAQ0EJhYkT3BlblNTTCBHZW5lcmF0ZWQgU2VydmVyIENlcnRp\r\nZmljYXRlMB0GA1UdDgQWBBQwc1H9AL8pRlW2e5SLCfPPqtqc0DCBpQYDVR0jBIGd\r\nMIGagBRt6m6qqTcsPIktFz79Ru7DnnjtdKF+pHwwejELMAkGA1UEBhMCREUxGzAZ\r\nBgNVBAgMEkJhZGVuLVd1ZXJ0dGVtYmVyZzESMBAGA1UEBwwJU3R1dHRnYXJ0MRcw\r\nFQYDVQQKDA5OZXh0Y2xvdWQgR21iSDEhMB8GA1UEAwwYTmV4dGNsb3VkIFJvb3Qg\r\nQXV0aG9yaXR5ggIQADAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUH\r\nAwEwDQYJKoZIhvcNAQELBQADggEBADZ6+HV\/+0NEH3nahTBFxO6nKyR\/VWigACH0\r\nnaV0ecTcoQwDjKDNNFr+4S1WlHdwITlnNabC7v9rZ\/6QvbkrOTuO9fOR6azp1EwW\r\n2pixWqj0Sb9\/dSIVRpSq+jpBE6JAiX44dSR7zoBxRB8DgVO2Afy0s80xEpr5JAzb\r\nNYuPS7M5UHdAv2dr16fDcDIvn+vk92KpNh1NTeZFjBbRVQ9DXrgkRGW34TK8uSLI\r\nYG6jnfJ6eJgTaO431ywWPXNg1mUMaT\/+QBOgB299QVCKQU+lcZWptQt+RdsJUm46\r\nNY\/nARy4Oi4uOe88SuWITj9KhrFmEvrUlgM8FvoXA1ldrR7KiEg=\r\n-----END CERTIFICATE-----","signature": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15"}'

* **Returns**:

  * **HTTP 201**: If the app was not previously present and was registered successfully
  * **HTTP 204**: If the app has been updated (either owner or certificate change)
  * **HTTP 400**: If the app id contains invalid characters, the signature could not be validated or if the posted app certificate has been revoked
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to update the app signature (only owners are allowed to do so)

You can also use this route to register a new certificate for an app if you are the app owner. However keep in mind that this will delete all previous app releases, since their signatures are now invalid and not installable anymore.

Find out more how to generate and request the certificate signature by following the :ref:`developer-guide`.

.. note:: **DO NOT** post your private key which is stored in the **.key** file. The private certificate needs to be stored securely. If you are unsure whether a file is a private certificate or the public one: your private certificate's content starts with **-----BEGIN PRIVATE KEY-----**, whereas your public certificate's content starts with **-----BEGIN CERTIFICATE-----**

.. note:: Keep in mind that we verify that the posted certificate and the signature are valid: the certificate needs to be signed by us and your app id signature must stem from the same certificate and match the expected result.

.. _api-create-release:

Publish a New App Release
~~~~~~~~~~~~~~~~~~~~~~~~~
The following request will create a new app release or update an existing release:

* **Url**: POST /api/v1/apps/releases

* **Authentication** Basic, Token

* **Content-Type**: application/json

* **Request body**:

  * **download**: An Https (Http is not allowed!) link to the archive packaged (maximum size: 20 Megabytes) as tar.gz, info.xml must be smaller than 512Kb
  * **signature**: A SHA512 signature over the archive using the app's certificate, can be created using::

        openssl dgst -sha512 -sign ~/.nextcloud/certificates/APP_ID.key /path/to/app.tar.gz | openssl base64

  * **nightly (Optional)**: If true this release will be stored as a nightly. All previous nightly releases will be deleted.

  .. code-block:: json

      {
          "download": "https://example.com/release.tar.gz",
          "signature": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15",
          "nightly": false
      }


* **Example CURL request**::

        curl -X POST -u "user:password" https://apps.nextcloud.com/api/v1/apps/releases -H "Content-Type: application/json" -d '{"download":"https://example.com/release.tar.gz", "signature": "65e613318107bceb131af5cf8b71e773b79e1a9476506f502c8e2017b52aba15"}'

* **Returns**:

  * **HTTP 200**: If the app release was updated successfully
  * **HTTP 201**: If the app release was created successfully
  * **HTTP 400**: If the app release contains invalid data, is too large, is not registered yet, the signature could not be validated, the current app certificate has been revoked or could not be downloaded from the provided link
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to create or update the app release

If there is no app with the given app id yet it will fail: you need to :ref:`register your app id first <api-register-app>`. Then the **info.xml** file which lies in the compressed archive's folder **app-id/appinfo/info.xml** is being parsed and validated. Afterwards the provided signature will be validated using the app's certificate and the downloaded archive's SHA512 checksum. The validated result is then saved in the database. Both owners and co-maintainers are allowed to upload new releases.

If the app release version is the latest version, everything is updated. If it's not the latest release, only release relevant details are updated. This **excludes** the following info.xml elements:

  * name
  * summary
  * description
  * category
  * author
  * documentation
  * bugs
  * website
  * screenshot


For more information about validation and which **info.xml** fields are parsed, see :ref:`app-metadata`

.. _api-delete-release:

Delete an App Release
~~~~~~~~~~~~~~~~~~~~~
Only app owners or co-maintainers are allowed to delete an app release. The owner is the user that pushes the first release of an app to the store.

* **Url**: DELETE /api/v1/apps/{**app-id**}/releases/{**app-version**}

* **Url parameters**:

 * **app-id**: app id, lower case ASCII characters and underscores are allowed
 * **app-version**: app version, semantic version, digits only

* **Authentication**: Basic, Token

* **Authorization**: App owners and co-maintainers

* **Example CURL request**::

    curl -X DELETE https://apps.nextcloud.com/api/v1/apps/news/releases/9.0.0 -u "user:password"


* **Returns**:

  * **HTTP 204**: If the app release was deleted successfully
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app release
  * **HTTP 404**: If the app release could not be found

.. _api-delete-nightly-release:

Delete a Nightly App Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Only app owners or co-maintainers are allowed to delete a nightly app release. The owner is the user that pushes the first release of an app to the store.

* **Url**: DELETE /api/v1/apps/{**app-id**}/releases/nightly/{**app-version**}

* **Url parameters**:

 * **app-id**: app id, lower case ASCII characters and underscores are allowed
 * **app-version**: app version, semantic version, digits only

* **Authentication**: Basic, Token

* **Authorization**: App owners and co-maintainers

* **Example CURL request**::

    curl -X DELETE https://apps.nextcloud.com/api/v1/apps/news/releases/nightly/9.0.0 -u "user:password"


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

* **Url**: GET /api/v1/ratings.json

* **Authentication**: None

* **Caching**: `ETag <https://en.wikipedia.org/wiki/HTTP_ETag>`_

* **Example CURL request**::

    curl https://apps.nextcloud.com/api/v1/ratings.json -H 'If-None-Match: ""1-2016-09-03 17:11:38.772856+00:00""'

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

.. _api-get-app-discover:

Get the app discover data
~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

For the specification of the data format see :ref:`app-discover`.
