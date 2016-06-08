import base64

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from nextcloudappstore.core.models import App, AppRelease
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.test import APIClient


class AppTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test',
                                             email='test@test.com')
        self.api_client = APIClient()

    def _login(self, user='test', password='test'):
        credentials = '%s:%s' % (user, password)
        base64_credentials = base64.b64encode(
            credentials.encode(HTTP_HEADER_ENCODING)
        ).decode(HTTP_HEADER_ENCODING)
        auth = 'Basic %s' % base64_credentials
        self.api_client.credentials(HTTP_AUTHORIZATION=auth)

    def test_apps(self):
        url = reverse('api-v1:apps', kwargs={'version': '9.1.0'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)

    def test_delete(self):
        self.api_client.login(username='test', password='test')
        App.objects.create(id='news', owner=self.user)
        url = reverse('api-v1:app-delete', kwargs={'pk': 'news'})
        self._login()
        response = self.api_client.delete(url)
        self.assertEqual(204, response.status_code)

    def test_delete_unauthenticated(self):
        App.objects.create(id='news', owner=self.user)
        url = reverse('api-v1:app-delete', kwargs={'pk': 'news'})
        response = self.api_client.delete(url)
        self.assertEqual(401, response.status_code)

    def test_delete_unauthorized(self):
        owner = User.objects.create_user(username='owner', password='owner',
                                         email='owner@owner.com')
        App.objects.create(id='news', owner=owner)
        url = reverse('api-v1:app-delete', kwargs={'pk': 'news'})
        self._login()
        response = self.api_client.delete(url)
        self.assertEqual(403, response.status_code)

    def test_delete_not_found(self):
        self.api_client.login(username='test', password='test')
        url = reverse('api-v1:app-delete', kwargs={'pk': 'news'})
        self._login()
        response = self.api_client.delete(url)
        self.assertEqual(404, response.status_code)

    def test_releases_platform_min(self):
        app = App.objects.create(pk='news', owner=self.user)
        AppRelease.objects.create(app=app, version='10.1',
                                  platform_min_version='9.1.1')
        url = reverse('api-v1:apps', kwargs={'version': '9.1.0'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_min_max(self):
        app = App.objects.create(pk='news', owner=self.user)
        AppRelease.objects.create(app=app, version='10.1',
                                  platform_min_version='9.1.1',
                                  platform_max_version='9.1.1')
        url = reverse('api-v1:apps', kwargs={'version': '9.1.2'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_max(self):
        app = App.objects.create(pk='news', owner=self.user)
        AppRelease.objects.create(app=app, version='10.1',
                                  platform_max_version='9.1.1')
        url = reverse('api-v1:apps', kwargs={'version': '9.1.2'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_releases_platform_max_wildcard(self):
        app = App.objects.create(pk='news', owner=self.user)
        AppRelease.objects.create(app=app, version='10.1',
                                  platform_max_version='9.1')
        url = reverse('api-v1:apps', kwargs={'version': '9.1.2'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_releases_platform_ok(self):
        app = App.objects.create(pk='news', owner=self.user)
        AppRelease.objects.create(app=app, version='10.1',
                                  platform_max_version='9.1.1',
                                  platform_min_version='9.1.1')
        url = reverse('api-v1:apps', kwargs={'version': '9.1.1'})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def tearDown(self):
        self.user.delete()
