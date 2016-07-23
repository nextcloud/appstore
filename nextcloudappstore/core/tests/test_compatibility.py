from django.contrib.auth import get_user_model
from django.test import TestCase
from nextcloudappstore.core.models import App, AppRelease


class CompatibilityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='test',
                                                         email='test@test.com')

        self.platform_versions = ['9.0', '9.1', '9.2', '10.0', '10.1']

        self.app1 = App.objects.create(pk='news', owner=self.user)
        self.app1.set_current_language('en')
        self.app1.name = 'News'
        self.app1.description = 'RSS feed reader'
        self.app1.save()
        AppRelease.objects.create(app=self.app1, version='1.0.0',
                                  platform_version_spec='>=9.0.0,<9.1.0')
        AppRelease.objects.create(app=self.app1, version='2.0.0',
                                  platform_version_spec='>=9.0.5,<9.1.5')
        AppRelease.objects.create(app=self.app1, version='3.0.0',
                                  platform_version_spec='>=9.1.0,<10.0.0')
        AppRelease.objects.create(app=self.app1, version='4.0.0',
                                  platform_version_spec='>=9.2.0')
        AppRelease.objects.create(app=self.app1, version='5.0.0',
                                  platform_version_spec='>=10.0.0')
        AppRelease.objects.create(app=self.app1, version='6.0.0-nightly',
                                  platform_version_spec='>=10.0.0')

        self.app2 = App.objects.create(pk='notes', owner=self.user)
        self.app2.set_current_language('en')
        self.app2.name = 'Notes'
        self.app2.description = 'Notes application'
        self.app2.save()
        AppRelease.objects.create(app=self.app2, version='1.0.0',
                                  platform_version_spec='>=9.0.0,<9.1.0')
        AppRelease.objects.create(app=self.app2, version='2.0.0',
                                  platform_version_spec='>=9.1.0,<9.2.0')
        AppRelease.objects.create(app=self.app2, version='3.0.0',
                                  platform_version_spec='>=9.2.0,<10.0.0')
        AppRelease.objects.create(app=self.app2, version='4.0.0',
                                  platform_version_spec='>=9.2.0,<10.0.0')

    def tearDown(self):
        self.app1.delete()
        self.app2.delete()
        self.user.delete()

    def test_compatible_apps(self):
        apps = App.objects.get_compatible('10.0.0')
        apps2 = App.objects.get_compatible('9.2.0')
        apps3 = App.objects.get_compatible('9.1.0')
        apps4 = App.objects.get_compatible('9.0.0')
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].id, self.app1.id)
        self.assertEqual(len(apps2), 2)
        self.assertEqual(len(apps3), 2)
        self.assertEqual(len(apps4), 2)

    def test_compatible_releases(self):
        app1rel = self.app1.compatible_releases('10.0.0')
        app1rel2 = self.app1.compatible_releases('9.0.0')
        app2rel = self.app2.compatible_releases('9.1.0')
        app2rel2 = self.app2.compatible_releases('9.0.0')
        self.assertEqual(len(app1rel), 2)
        self.assertEqual(len(app1rel2), 1)
        self.assertEqual(len(app2rel), 1)
        self.assertEqual(len(app2rel2), 1)

    def test_compatible_releases_by_platform_v(self):
        with self.settings(PLATFORM_VERSIONS=self.platform_versions):
            app1 = self.app1.latest_releases_by_platform_v()
            app2 = self.app2.latest_releases_by_platform_v()
            self.assertEqual(app1['9.0'].version, '2.0.0')
            self.assertEqual(app1['9.1'].version, '3.0.0')
            self.assertEqual(app1['9.2'].version, '4.0.0')
            self.assertEqual(app1['10.0'].version, '5.0.0')
            self.assertEqual(app2['9.0'].version, '1.0.0')
            self.assertEqual(app2['9.1'].version, '2.0.0')
            self.assertEqual(app2['9.2'].version, '4.0.0')
            self.assertEqual(app2['10.0'], None)

    def test_correct_comparison_and_ignore_nightly(self):
        with self.settings(PLATFORM_VERSIONS=self.platform_versions):
            app1 = self.app1.latest_releases_by_platform_v()
            self.assertEqual(app1['10.0'].version, '5.0.0')

    def test_nightlies(self):
        with self.settings(PLATFORM_VERSIONS=self.platform_versions):
            app1 = self.app1.compatible_nightly_releases('10.0')
            self.assertEqual(app1[0].version, '6.0.0-nightly')
            self.assertEqual(len(app1), 1)
