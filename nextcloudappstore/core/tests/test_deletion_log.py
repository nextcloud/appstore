from django.contrib.auth import get_user_model
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRelease, AppReleaseDeleteLog


class DeletionLogTest(TestCase):
    def test_delete_app(self):
        user = get_user_model().objects.create(username='john')
        app = App.objects.create(owner=user, id='news')
        self.assertEqual(0, AppReleaseDeleteLog.objects.count())

        app.delete()
        self.assertEqual(1, AppReleaseDeleteLog.objects.count())

    def test_delete_owner(self):
        user = get_user_model().objects.create(username='john')
        App.objects.create(owner=user, id='news')
        self.assertEqual(0, AppReleaseDeleteLog.objects.count())

        user.delete()
        self.assertEqual(1, AppReleaseDeleteLog.objects.count())

    def test_delete_app_release(self):
        user = get_user_model().objects.create(username='john')
        app = App.objects.create(owner=user, id='news')
        release = AppRelease.objects.create(app=app, version='1.0.0')
        self.assertEqual(0, AppReleaseDeleteLog.objects.count())

        release.delete()
        self.assertEqual(1, AppReleaseDeleteLog.objects.count())
