from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from nextcloudappstore.core.api.v1.tests.api import ApiTest
from nextcloudappstore.core.models import App, AppRelease


class AppReleaseTest(ApiTest):
    delete_url = reverse('api-v1:app-release-delete',
                         kwargs={'app': 'news', 'version': '9.0.0'})

    def create_release(self, owner, version='9.0.0', co_maintainers=[]):
        app = App.objects.create(id='news', owner=owner)
        app.co_maintainers = co_maintainers
        app.save()
        return AppRelease.objects.create(version=version, app=app)

    def test_delete(self):
        self.create_release(self.user)
        self._login()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(AppRelease.DoesNotExist):
            AppRelease.objects.get(version='9.0.0', app__id='news')

    def test_delete_unauthenticated(self):
        self.create_release(self.user)
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(401, response.status_code)

    def test_delete_unauthorized(self):
        owner = User.objects.create_user(username='owner', password='owner',
                                         email='owner@owner.com')
        self.create_release(owner)
        self._login()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(403, response.status_code)

    def test_delete_co_maintainer(self):
        owner = User.objects.create_user(username='owner', password='owner',
                                         email='owner@owner.com')
        self.create_release(owner=owner, co_maintainers=[self.user])
        self._login()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(204, response.status_code)
        with self.assertRaises(AppRelease.DoesNotExist):
            AppRelease.objects.get(version='9.0.0', app__id='news')

    def test_delete_not_found(self):
        self.api_client.login(username='test', password='test')
        self._login()
        response = self.api_client.delete(self.delete_url)
        self.assertEqual(404, response.status_code)
