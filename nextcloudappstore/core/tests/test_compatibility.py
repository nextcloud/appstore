from django.contrib.auth import get_user_model
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRelease, NextcloudRelease


class CompatibilityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")

        self.platform_versions = ["9.0.0", "9.0.5", "10.0.0", "11.0.0", "12.0.0", "13.0.0"]

        self.app1 = App.objects.create(pk="news", owner=self.user)
        self.app1.set_current_language("en")
        self.app1.name = "News"
        self.app1.description = "RSS feed reader"
        self.app1.save()

    def tearDown(self):
        if hasattr(self, "app1"):
            self.app1.delete()
        if hasattr(self, "app2"):
            self.app2.delete()
        self.user.delete()

    def test_compatible_apps_deduplication(self):
        AppRelease.objects.create(app=self.app1, version="1.0.0", platform_version_spec=">=9.0.0,<10.0.0")
        AppRelease.objects.create(app=self.app1, version="2.0.0", platform_version_spec=">=10.0.0,<11.0.0")
        AppRelease.objects.create(app=self.app1, version="3.0.0", platform_version_spec=">=10.0.0,<11.0.0")
        NextcloudRelease.objects.create(version="9.0.0")
        NextcloudRelease.objects.create(version="9.0.1")
        NextcloudRelease.objects.create(version="9.0.2")
        NextcloudRelease.objects.create(version="10.0.0")
        releases = self.app1.releases_by_platform_v()
        self.assertEqual(1, len(releases["9"]))
        self.assertEqual(2, len(releases["10"]))

    def test_compatible_apps(self):
        self._create_example_releases()
        apps = App.objects.get_compatible("12.0.0")
        apps2 = App.objects.get_compatible("11.0.0")
        apps3 = App.objects.get_compatible("10.0.0")
        apps4 = App.objects.get_compatible("9.0.0")
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].id, self.app1.id)
        self.assertEqual(len(apps2), 2)
        self.assertEqual(len(apps3), 2)
        self.assertEqual(len(apps4), 2)

    def test_compatible_releases(self):
        self._create_example_releases()
        app1rel = self.app1.compatible_releases("12.0.0")
        app1rel2 = self.app1.compatible_releases("9.0.0")
        app2rel = self.app2.compatible_releases("10.0.0")
        app2rel2 = self.app2.compatible_releases("9.0.0")
        self.assertEqual(len(app1rel), 2)
        self.assertEqual(len(app1rel2), 1)
        self.assertEqual(len(app2rel), 1)
        self.assertEqual(len(app2rel2), 1)

    def test_compatible_unstable_releases(self):
        self._create_example_releases()
        app1 = self.app1.compatible_unstable_releases("12.0")
        app2 = self.app2.compatible_unstable_releases("12.0")
        self.assertEqual(app1[0].version, "6.0.0")
        self.assertEqual(app1[0].is_nightly, True)
        self.assertEqual(app1[1].version, "6.0.0-alpha")
        self.assertEqual(len(app1), 2)
        self.assertEqual(app2, [])

    def test_compatible_releases_by_platform_v(self):
        self._create_example_releases()
        self._create_nextcloud_versions()
        app1 = self.app1.latest_releases_by_platform_v()
        app2 = self.app2.latest_releases_by_platform_v()
        self.assertEqual(app1["9"]["stable"].version, "2.0.0")
        self.assertEqual(app1["9"]["unstable"], None)
        self.assertEqual(app1["10"]["stable"].version, "3.0.0")
        self.assertEqual(app1["10"]["unstable"], None)
        self.assertEqual(app1["11"]["stable"].version, "4.0.0")
        self.assertEqual(app1["11"]["unstable"], None)
        self.assertEqual(app1["12"]["stable"].version, "5.0.0")
        self.assertEqual(app1["12"]["unstable"].version, "6.0.0")
        self.assertEqual(app1["12"]["unstable"].is_nightly, True)
        self.assertEqual(app2["9"]["stable"].version, "1.0.0")
        self.assertEqual(app2["10"]["stable"].version, "2.0.0")
        self.assertEqual(app2["11"]["stable"].version, "4.0.0")
        self.assertEqual(app2["12"]["stable"], None)

    def test_correct_comparison(self):
        self._create_example_releases()
        self._create_nextcloud_versions()
        app1 = self.app1.latest_releases_by_platform_v()
        self.assertEqual(app1["10"]["stable"].version, "3.0.0")
        self.assertEqual(app1["12"]["unstable"].version, "6.0.0")

    def _create_nextcloud_versions(self):
        for version in self.platform_versions:
            NextcloudRelease.objects.create(version=version)

    def _create_example_releases(self):
        AppRelease.objects.create(app=self.app1, version="1.0.0", platform_version_spec=">=9.0.0,<10.0.0")
        AppRelease.objects.create(app=self.app1, version="2.0.0", platform_version_spec=">=9.0.5,<10.0.5")
        AppRelease.objects.create(app=self.app1, version="3.0.0", platform_version_spec=">=10.0.0,<12.0.0")
        AppRelease.objects.create(app=self.app1, version="4.0.0", platform_version_spec=">=11.0.0")
        AppRelease.objects.create(app=self.app1, version="5.0.0", platform_version_spec=">=12.0.0")
        AppRelease.objects.create(app=self.app1, version="6.0.0-alpha", platform_version_spec=">=12.0.0")
        AppRelease.objects.create(app=self.app1, version="6.0.0", platform_version_spec=">=12.0.0", is_nightly=True)

        self.app2 = App.objects.create(pk="notes", owner=self.user)
        self.app2.set_current_language("en")
        self.app2.name = "Notes"
        self.app2.description = "Notes application"
        self.app2.save()
        AppRelease.objects.create(app=self.app2, version="1.0.0", platform_version_spec=">=9.0.0,<10.0.0")
        AppRelease.objects.create(app=self.app2, version="2.0.0", platform_version_spec=">=10.0.0,<11.0.0")
        AppRelease.objects.create(app=self.app2, version="3.0.0", platform_version_spec=">=11.0.0,<12.0.0")
        AppRelease.objects.create(app=self.app2, version="4.0.0", platform_version_spec=">=11.0.0,<12.0.0")
