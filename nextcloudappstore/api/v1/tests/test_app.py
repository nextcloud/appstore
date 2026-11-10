"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection, connections, transaction
from django.db.models.signals import post_init
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.api.v1.views import selectable_release_ids
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
            response = self.api_client.get(url, HTTP_X_NC_SUBSCRIPTION_KEY="invalid")
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertNotIn("enterprise", ids)

    def test_apps_includes_enterprise_with_valid_key(self):
        self._create_app_with_release("news")
        self._create_app_with_release("enterprise", is_enterprise_only=True)
        url = reverse("api:v1:apps")
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=True):
            response = self.api_client.get(url, HTTP_X_NC_SUBSCRIPTION_KEY="valid")
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
            response = self.api_client.get(url, HTTP_X_NC_SUBSCRIPTION_KEY="valid")
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
            response = self.api_client.get(url, HTTP_X_NC_SUBSCRIPTION_KEY="valid")
        self.assertEqual(200, response.status_code)
        ids = [app["id"] for app in response.data]
        self.assertIn("news", ids)
        self.assertIn("enterprise", ids)

    def _create_releases(self, app, releases):
        for version, platform, php, is_nightly in releases:
            AppRelease.objects.create(
                app=app,
                version=version,
                platform_version_spec=platform,
                raw_platform_version_spec=platform,
                php_version_spec=php,
                raw_php_version_spec=php,
                is_nightly=is_nightly,
            )

    def test_apps_lists_newest_release_per_requirement_set(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(
            app,
            (
                ("1.9.0", ">=25.0.0", "*", False),
                ("1.10.0", ">=25.0.0", "*", False),
                ("1.2.0", ">=25.0.0", ">=8.1.0", False),
                ("2.0.0", ">=26.0.0", "*", False),
                ("2.1.0-beta.1", ">=26.0.0", "*", False),
                ("2.1.0-beta.2", ">=26.0.0", "*", False),
                ("2.0.0", ">=26.0.0", "*", True),
            ),
        )
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        releases = {(release["version"], release["is_nightly"]) for release in response.data[0]["releases"]}
        self.assertEqual(
            {("1.10.0", False), ("1.2.0", False), ("2.0.0", False), ("2.1.0-beta.2", False), ("2.0.0", True)},
            releases,
        )

    def test_apps_keeps_releases_a_server_cannot_tell_apart(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(app, (("3.0.0-a.1", ">=26.0.0", "*", False), ("3.0.0-alpha.1", ">=26.0.0", "*", False)))
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        versions = {release["version"] for release in response.data[0]["releases"]}
        self.assertEqual({"3.0.0-a.1", "3.0.0-alpha.1"}, versions)

    def test_apps_keeps_a_set_php_versions_disagree_on(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(
            app,
            (
                ("2.0.0-alpha.5", ">=26.0.0", "*", False),
                ("2.0.0-alpha.6", ">=26.0.0", "*", False),
                ("2.0.0-", ">=26.0.0", "*", False),
            ),
        )
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        versions = {release["version"] for release in response.data[0]["releases"]}
        self.assertEqual({"2.0.0-alpha.5", "2.0.0-alpha.6", "2.0.0-"}, versions)

    def test_apps_keeps_the_newest_release_of_each_app(self):
        news = App.objects.create(pk="news", owner=self.user)
        mail = App.objects.create(pk="mail", owner=self.user)
        self._create_releases(news, (("1.0.0", ">=26.0.0", "*", False), ("2.0.0", ">=26.0.0", "*", False)))
        self._create_releases(mail, (("1.5.0", ">=26.0.0", "*", False), ("1.6.0", ">=26.0.0", "*", False)))
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        releases = {app["id"]: [release["version"] for release in app["releases"]] for app in response.data}
        self.assertEqual({"news": ["2.0.0"], "mail": ["1.6.0"]}, releases)

    def test_apps_keeps_a_nightly_lower_than_the_stable_release(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(app, (("2.0.0", ">=26.0.0", "*", False), ("1.9.0", ">=26.0.0", "*", True)))
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        releases = {(release["version"], release["is_nightly"]) for release in response.data[0]["releases"]}
        self.assertEqual({("2.0.0", False), ("1.9.0", True)}, releases)

    def test_apps_leaves_out_exapp_releases(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(app, (("1.0.0", ">=26.0.0", "*", False),))
        AppRelease.objects.create(
            app=app,
            version="2.0.0",
            platform_version_spec=">=26.0.0",
            raw_platform_version_spec=">=26.0.0",
            php_version_spec="*",
            raw_php_version_spec="*",
            aa_is_system=False,
        )
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(["1.0.0"], [release["version"] for release in response.data[0]["releases"]])

    def test_apps_loads_only_the_releases_it_lists(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(
            app,
            (("1.8.0", ">=26.0.0", "*", False), ("1.9.0", ">=26.0.0", "*", False), ("1.10.0", ">=26.0.0", "*", False)),
        )
        loaded = []

        def record(sender, instance, **kwargs):
            loaded.append(instance.version)

        post_init.connect(record, sender=AppRelease)
        self.addCleanup(post_init.disconnect, record, sender=AppRelease)
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(["1.10.0"], loaded)

    def test_apps_lists_a_stable_release_before_a_nightly_of_the_same_version(self):
        # Created in both orders, so the result cannot come from the order of the rows.
        news = App.objects.create(pk="news", owner=self.user)
        mail = App.objects.create(pk="mail", owner=self.user)
        self._create_releases(news, (("1.0.0", ">=26.0.0", "*", True), ("1.0.0", ">=26.0.0", "*", False)))
        self._create_releases(mail, (("1.0.0", ">=26.0.0", "*", False), ("1.0.0", ">=26.0.0", "*", True)))
        response = self.api_client.get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        releases = {
            app["id"]: [(release["version"], release["is_nightly"]) for release in app["releases"]]
            for app in response.data
        }
        self.assertEqual(
            {"news": [("1.0.0", False), ("1.0.0", True)], "mail": [("1.0.0", False), ("1.0.0", True)]}, releases
        )

    def test_apps_picks_the_releases_once_per_request(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(app, (("1.0.0", ">=26.0.0", "*", False),))
        with patch("nextcloudappstore.api.v1.views.selectable_release_ids", wraps=selectable_release_ids) as selectable:
            response = self.api_client.get(reverse("api:v1:apps"), HTTP_ACCEPT="text/html")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, selectable.call_count)

    def test_platform_lists_every_compatible_release(self):
        app = App.objects.create(pk="news", owner=self.user)
        self._create_releases(app, (("1.9.0", ">=9.1.1", "*", False), ("1.10.0", ">=9.1.1", "*", False)))
        response = self.api_client.get(reverse("api:v1:app", kwargs={"version": "9.1.1"}))
        self.assertEqual(200, response.status_code)
        versions = {release["version"] for release in response.data[0]["releases"]}
        self.assertEqual({"1.9.0", "1.10.0"}, versions)

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


@skipUnless(connection.vendor == "postgresql", "SQLite reads a whole transaction from one snapshot")
class AppsSnapshotTest(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")
        self.app = App.objects.create(pk="news", owner=self.user)
        self.other_connection = connections.create_connection("default")
        self.addCleanup(self.other_connection.close)

    def test_apps_keeps_a_release_deleted_while_it_builds(self):
        for version in ("1.9.0", "1.10.0"):
            AppRelease.objects.create(
                app=self.app,
                version=version,
                platform_version_spec=">=26.0.0",
                raw_platform_version_spec=">=26.0.0",
                php_version_spec="*",
                raw_php_version_spec="*",
            )

        def ids_then_delete_newest():
            ids = selectable_release_ids()
            with self.other_connection.cursor() as cursor:
                cursor.execute("DELETE FROM core_apprelease WHERE version = %s", ["1.10.0"])
            return ids

        with patch("nextcloudappstore.api.v1.views.selectable_release_ids", ids_then_delete_newest):
            response = APIClient().get(reverse("api:v1:apps"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(["1.10.0"], [release["version"] for release in response.data[0]["releases"]])

    def test_apps_works_inside_a_transaction_without_autocommit(self):
        AppRelease.objects.create(
            app=self.app,
            version="1.0.0",
            platform_version_spec=">=26.0.0",
            raw_platform_version_spec=">=26.0.0",
            php_version_spec="*",
            raw_php_version_spec="*",
        )
        transaction.set_autocommit(False)
        try:
            App.objects.count()
            response = APIClient().get(reverse("api:v1:apps"))
        finally:
            transaction.rollback()
            transaction.set_autocommit(True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(["1.0.0"], [release["version"] for release in response.data[0]["releases"]])
