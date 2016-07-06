from django.contrib.auth import get_user_model
from django.test import TestCase
from nextcloudappstore.core.models import App, AppRelease


class CompatibilityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='test',
                                                         email='test@test.com')

        self.platform_versions = ['9.0.0', '9.0.5', '9.1.3', '10.0.0']

        self.app1 = App.objects.create(pk='news', owner=self.user)
        self.app1.set_current_language('en')
        self.app1.name = 'News'
        self.app1.description = 'RSS feed reader'
        self.app1.save()
        AppRelease.objects.create(app=self.app1, version='1.0.0',
                                  platform_version_spec='>=9.0.0')
        AppRelease.objects.create(app=self.app1, version='1.1.3',
                                  platform_version_spec='>=9.0.0,<9.1.5')
        AppRelease.objects.create(app=self.app1, version='2.0.7',
                                  platform_version_spec='>=9.1.5')
        AppRelease.objects.create(app=self.app1, version='3.1.11',
                                  platform_version_spec='>=10.0.0')

        self.app2 = App.objects.create(pk='notes', owner=self.user)
        self.app2.set_current_language('en')
        self.app2.name = 'Notes'
        self.app2.description = 'Notes application'
        self.app2.save()
        AppRelease.objects.create(app=self.app2, version='3.2.2',
                                  platform_version_spec='>=9.0.0,<9.1.3')
        AppRelease.objects.create(app=self.app2, version='3.6.0',
                                  platform_version_spec='>=9.0.5,<9.1.3')
        AppRelease.objects.create(app=self.app2, version='4.1.2',
                                  platform_version_spec='>=9.0.5,<9.1.3')
        AppRelease.objects.create(app=self.app2, version='4.3.5',
                                  platform_version_spec='>=9.1.5,<10.0.1')

    def tearDown(self):
        self.app1.delete()
        self.app2.delete()
        self.user.delete()

    def test_compatible_apps(self):
        apps = App.objects.get_compatible('10.0.0')
        self.assertEqual(apps[0].id, self.app1.id)

    def test_compatible_releases(self):
        app1rel = self.app1.compatible_releases('10.0.0')
        app1rel2 = self.app1.compatible_releases('9.0.0')
        app2rel = self.app2.compatible_releases('9.1.2')
        app2rel2 = self.app2.compatible_releases('9.0.0')
        self.assertEqual(len(app1rel), 3)
        self.assertEqual(len(app1rel2), 2)
        self.assertEqual(len(app2rel), 3)
        self.assertEqual(len(app2rel2), 1)

    def test_compatible_releases_by_platform_v(self):
        with self.settings(PLATFORM_VERSIONS=self.platform_versions):
            app1 = self.app1.latest_releases_by_platform_v()
            app2 = self.app2.latest_releases_by_platform_v()
            self.assertEqual(app1['9.0.0'].version, '1.1.3')
            self.assertEqual(app1['9.0.5'].version, '1.1.3')
            self.assertEqual(app1['9.1.3'].version, '1.1.3')
            self.assertEqual(app1['10.0.0'].version, '3.1.11')
            self.assertEqual(app2['9.0.0'].version, '3.2.2')
            self.assertEqual(app2['9.0.5'].version, '4.1.2')
            self.assertEqual(app2['9.1.3'], None)
            self.assertEqual(app2['10.0.0'].version, '4.3.5')
