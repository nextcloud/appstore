from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib import auth


class AppTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test',
                                             email='test@test.com')

    def test_apps(self):
        url = reverse('api-v1:apps', kwargs={'version': '9.1'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_login(self):
        self.client.login(username='test', password='test')
        user = auth.get_user(self.client)
        self.assertEqual('test', user.username)
        self.client.logout()

    def tearDown(self):
        self.user.delete()
