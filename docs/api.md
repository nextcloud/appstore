# API (v1)
This is a draft and will continuously be updated :)


## Get All Apps And Their Releases For a Platform Release
This is the route that will return all releases to display inside Nextcloud's apps admin area. Future releases will add Http caching.

* **Url**: GET /api/v1/platform/{platform-version}/apps.json
  * **Parameters**:
    * **platform-version**: semantic version, digits only: Returns all the apps and their releases that work on this version. If an app has no working releases, the app will be excluded
* **Example CURL request**:

      curl http://localhost:8000/api/v1/platform/9.0.0/apps.json

* **Authentication**: None

* **Returns**: application/json
    ```json
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
                    "libs": [
                        {
                            "id": "libxml",
                            "minVersion": "3",
                            "maxVersion": "4"
                        }
                    ],
                    "databases": [
                        {
                            "id": "sqlite",
                            "name": "Sqlite",
                            "minVersion": "1",
                            "maxVersion": "2"
                        }
                    ],
                    "shellCommands": [
                        "grep"
                    ],
                    "phpMinVersion": "5.6",
                    "phpMaxVersion": "",
                    "platformMinVersion": "9.0",
                    "platformMaxVersion": "",
                    "minIntSize": 64,
                    "download": "http://127.0.0.1:8000/download",
                    "created": "2016-06-09T17:57:00.587076Z",
                    "lastModified": "2016-06-09T17:57:00.587238Z"
                }
            ],
            "authors": [
                {
                    "name": "Bernhard Posselt",
                    "mail": "ray@ray.com",
                    "homepage": "http://posselt.at"
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
    ```

Translated fields are stored inside a translations object. They can have any size, depending on if there is a translation. If a required language is not found, you should fall back to English.

Required versions (minimum and maximum versions) are stored in String fields. If a field is empty, this means that there is no version requirement. Minimum and maximum versions are inclusive, e.g. if your app works only on PHP 5.5 and 5.6, the minimum version will be 5.5.0 while the maximum version will be 5.6.*

## Delete An App
Only app owners are allowed to delete an app. The owner is the user that pushes the first release of an app to the store.

Deleting an app will also delete all releases which are associated with it.

* **Url**: DELETE /api/v1/apps/{app-id}
  * **Parameters**:
    * **app-id**: app id, lower case ASCII characters and underscores are allowed
* **Example CURL request**:

      curl -X DELETE http://localhost:8000/api/v1/apps/news

* **Authentication**: Basic

* **Returns**:
  * **HTTP 204**: If the app was deleted successfully
  * **HTTP 400**: If the app could not be found
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app

## Delete An App Release
Only app owners or co-maintainers are allowed to delete an app release. The owner is the user that pushes the first release of an app to the store.


* **Url**: DELETE /api/v1/apps/{app-id}/{app-version}
  * **Parameters**:
    * **app-id**: app id, lower case ASCII characters and underscores are allowed
    * **app-version**: app version, semantic version, digits only
* **Example CURL request**:

      curl -X DELETE http://localhost:8000/api/v1/apps/news/9.0.0

* **Authentication**: Basic

* **Returns**:
  * **HTTP 204**: If the app release was deleted successfully
  * **HTTP 400**: If the app release could not be found
  * **HTTP 401**: If the user is not authenticated
  * **HTTP 403**: If the user is not authorized to delete the app release

