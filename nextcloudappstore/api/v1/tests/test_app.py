"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.models import App, AppRelease


class AppTest(ApiTest):
    def test_apps(self):
        url = reverse("api:v1:app", kwargs={"version": "9.1.0"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)

    def _create_app_with_release(self, pk, is_enterprise_only=False, aa_is_system=None):
        app = App.objects.create(pk=pk, owner=self.user, is_enterprise_only=is_enterprise_only)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec=">=9.1.1", aa_is_system=aa_is_system)
        return app

    def test_apps_excludes_enterprise_by_default(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:apps")
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertNotIn("enterprise", ids)

    def test_apps_excludes_enterprise_with_invalid_key(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:apps")
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=False):
            response = self.api_client.get(url, {"subscription_key": "invalid"})
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertNotIn("enterprise", ids)

    def test_apps_includes_enterprise_with_valid_key(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:apps")
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=True):
            response = self.api_client.get(url, {"subscription_key": "valid"})
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertIn("enterprise", ids)

    def test_platform_excludes_enterprise_by_default(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:app", kwargs={"version": "9.1.1"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertNotIn("enterprise", ids)

    def test_platform_includes_enterprise_with_valid_key(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:app", kwargs={"version": "9.1.1"})
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=True):
            response = self.api_client.get(url, {"subscription_key": "valid"})
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertIn("enterprise", ids)

    def test_appapi_excludes_enterprise_by_default(self):
        self._create_app_with_release("news", aa_is_system=False)
        self._create_app_with_release("enterprise", is_enterprise_only=True, aa_is_system=False)
        url = reverse("api:v1:appapi_apps")
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertNotIn("enterprise", ids)

    def test_appapi_includes_enterprise_with_valid_key(self):
        self._create_app_with_release("news", aa_is_system=False)
        self._create_app_with_release("enterprise", is_enterprise_only=True, aa_is_system=False)
        url = reverse("api:v1:appapi_apps")
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=True):
            response = self.api_client.get(url, {"subscription_key": "valid"})
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertIn("enterprise", ids)

    def test_delete(self):
        App.objects.create(id="news", owner=self.user)
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})
        self._login_token()
        response = self.api_client.delete(url)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(App.DoesNotExist):
            App.objects.get(id="news")

    def test_delete_unauthenticated(self):
        App.objects.create(id="news", owner=self.user)
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})
        response = self.api_client.delete(url)
        self.assertEqual(401, response.status_code)

    def test_delete_unauthorized(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        App.objects.create(id="news", owner=owner)
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})
        self._login()
        response = self.api_client.delete(url)
        self.assertEqual(403, response.status_code)

    def test_delete_co_maintainer(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        app = App.objects.create(id="news", owner=owner)
        app.co_maintainers.add(self.user)
        app.save()
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})
        self._login_token()
        response = self.api_client.delete(url)
        self.assertEqual(403, response.status_code)

    def test_delete_not_found(self):
        self.api_client.login(username="test", password="test")
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})
        self._login()
        response = self.api_client.delete(url)
        self.assertEqual(404, response.status_code)

    def test_releases_platform_min(self):
        app = App.objects.create(pk="news", owner=self.user)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec=">=9.1.1")
        url = reverse("api:v1:app", kwargs={"version": "9.1.0"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_min_max(self):
        app = App.objects.create(pk="news", owner=self.user)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec=">=9.1.1,<9.1.2")
        url = reverse("api:v1:app", kwargs={"version": "9.1.2"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_max(self):
        app = App.objects.create(pk="news", owner=self.user)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec="<9.1.2")
        url = reverse("api:v1:app", kwargs={"version": "9.1.2"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_max_wildcard(self):
        app = App.objects.create(pk="news", owner=self.user)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec="<9.2.0")
        url = reverse("api:v1:app", kwargs={"version": "9.1.2"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_releases_platform_ok(self):
        app = App.objects.create(pk="news", owner=self.user)
        AppRelease.objects.create(app=app, version="10.1", platform_version_spec=">=9.1.1,<9.1.2")
        url = reverse("api:v1:app", kwargs={"version": "9.1.1"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def tearDown(self):
        self.user.delete()
