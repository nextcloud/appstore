from django.contrib.auth import get_user_model
from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.models import App, AppRelease


class AppRegisterTest(ApiTest):
    create_url = reverse("api:v1:app-register")
    _cert = read_relative_file(__file__, "../../../certificate/tests/data/certificates/news-old.crt").strip()

    def _create_app(self, owner, app_id):
        return App.objects.create(owner=owner, id=app_id)

    def test_register_unauthenticated(self):
        response = self.api_client.post(
            self.create_url, data={"signature": "sign", "certificate": "cert"}, format="json"
        )
        self.assertEqual(401, response.status_code)

    def test_register_unauthorized(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        self._create_app(owner, "news")
        self._login_token()
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url, data={"signature": "sign", "certificate": self._cert}, format="json"
            )
            self.assertEqual(403, response.status_code)

    def test_register_transfer(self):
        owner = get_user_model().objects.create_user(username="owner", password="owner", email="owner@owner.com")
        app = self._create_app(owner, "news")
        app.ownership_transfer_enabled = True
        app.save()
        self._login_token()
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url, data={"signature": "sign", "certificate": self._cert}, format="json"
            )
            self.assertEqual(204, response.status_code)
            app = App.objects.get(id="news")
            self.assertEqual(self.user, app.owner)
            self.assertFalse(app.ownership_transfer_enabled)

    def test_register(self):
        self._login()
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url, data={"signature": "sign", "certificate": self._cert}, format="json"
            )
            self.assertEqual(201, response.status_code)
            app = App.objects.get(id="news")
            self.assertEqual(self.user, app.owner)
            self.assertEqual(self._cert, app.certificate)

    def test_register_update(self):
        app = self._create_app(self.user, "news")
        app.certificate = "blubb"
        app.save()
        AppRelease.objects.create(version="1.0.0", app=app)

        self.assertEqual(1, App.objects.get(id="news").releases.all().count())
        self._login()
        with self.settings(VALIDATE_CERTIFICATES=False):
            response = self.api_client.post(
                self.create_url, data={"signature": "sign", "certificate": self._cert}, format="json"
            )
            self.assertEqual(204, response.status_code)
            app = App.objects.get(id="news")
            self.assertEqual(self.user, app.owner)
            self.assertEqual(self._cert, app.certificate)
            self.assertEqual(0, app.releases.all().count())
