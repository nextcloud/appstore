from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from nextcloudappstore.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.models import App, AppRelease


class AppReleaseTest(ApiTest):
    delete_url = reverse("api:v1:app-release-delete", kwargs={"app": "news", "version": "9.0.0"})
    delete_url_nightly = reverse(
        "api:v1:app-release-delete", kwargs={"app": "news", "version": "9.0.0", "nightly": "nightly"}
    )
    create_url = reverse("api:v1:app-release-create")
    app_args = {
        "app": {
            "id": "news",
            "release": {
                "version": "9.0.0",
                "platform_min_version": "9.0.0",
                "raw_platform_min_version": "9.0.0",
                "platform_max_version": "*",
                "raw_platform_max_version": "*",
                "php_min_version": "5.6.0",
                "raw_php_min_version": "5.6.0",
                "php_max_version": "*",
                "raw_php_max_version": "*",
            },
        }
    }

    def create_release(self, owner, version="9.0.0", co_maintainers=[]):
        app = App.objects.create(id="news", owner=owner)
        app.co_maintainers.set(co_maintainers)
        app.save()
        return AppRelease.objects.create(version=version, app=app)

    def test_delete(self):
        self.create_release(self.user)
        self._login_token()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(AppRelease.DoesNotExist):
            AppRelease.objects.get(version="9.0.0", app__id="news")

    def test_delete_unauthenticated(self):
        self.create_release(self.user)
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(401, response.status_code)

    def test_delete_unauthorized(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self.create_release(owner)
        self._login_token()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(403, response.status_code)

    def test_delete_not_found_token(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self.create_release(owner)
        self._login_token()
        response = self.api_client.delete(self.delete_url_nightly)
        self.assertEqual(404, response.status_code)

    def test_delete_co_maintainer(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self.create_release(owner=owner, co_maintainers=[self.user])
        self._login_token()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(AppRelease.DoesNotExist):
            AppRelease.objects.get(version="9.0.0", app__id="news")

    def test_delete_not_found(self):
        self._login()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(404, response.status_code)

    def test_create_unauthenticated(self):
        self.create_release(self.user)
        response = self.api_client.post(self.create_url, data={"download": "https://download.com"}, format="json")
        self.assertEqual(401, response.status_code)

    @patch.object(AppReleaseProvider, "get_release_info")
    def test_create_unauthorized(self, get_release_info):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self.create_release(owner)
        self._login()

        get_release_info.return_value = (self.app_args, "checksum")
        response = self.api_client.post(
            self.create_url,
            data={
                "download": "https://download.com",
                "signature": "sign",
            },
            format="json",
        )
        self.assertEqual(403, response.status_code)

    @patch.object(AppReleaseProvider, "get_release_info")
    def test_create_co_maintainer(self, get_release_info):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self.create_release(owner=owner, co_maintainers=[self.user])
        self._login()

        get_release_info.return_value = (self.app_args, "checksum")
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url,
                data={
                    "download": "https://download.com",
                    "signature": "sign",
                },
                format="json",
            )
            self.assertEqual(200, response.status_code)
            AppRelease.objects.get(version="9.0.0", app__id="news")

    @patch.object(AppReleaseProvider, "get_release_info")
    def test_no_app(self, get_release_info):
        self._login()
        get_release_info.return_value = (self.app_args, "checksum")
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url,
                data={
                    "download": "https://download.com",
                    "signature": "sign",
                },
                format="json",
            )
            self.assertEqual(400, response.status_code)
            with self.assertRaises(AppRelease.DoesNotExist):
                AppRelease.objects.get(version="9.0.0", app__id="news")

    def test_create_validate_https(self):
        self._login_token()
        response = self.api_client.post(
            self.create_url,
            data={
                "download": "http://download.com",
                "signature": "sign",
            },
            format="json",
        )
        self.assertEqual(400, response.status_code)
