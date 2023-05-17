from django.contrib.auth import get_user_model
from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.models import App, AppRelease


class AppTest(ApiTest):
    def test_apps(self):
        url = reverse("api:v1:app", kwargs={"version": "9.1.0"})
        response = self.api_client.get(url)
        self.assertEqual(200, response.status_code)

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
