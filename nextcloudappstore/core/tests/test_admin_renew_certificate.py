"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from nextcloudappstore.core.models import App, AppRelease


def _key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _cert(key, serial: int, cn: str = "news", days: int = 365) -> str:
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(serial)
        .not_valid_before(now - datetime.timedelta(days=400))
        .not_valid_after(now + datetime.timedelta(days=days))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode()


@override_settings(VALIDATE_CERTIFICATES=False)
class RenewCertificateAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.key = _key()
        cls.other_key = _key()

    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="admin", email="admin@example.com")
        self.owner = User.objects.create(username="owner", password="owner")
        self.app = App.objects.create(id="news", certificate=_cert(self.key, 1), owner=self.owner)
        AppRelease.objects.create(version="1.0.0", app=self.app)
        AppRelease.objects.create(version="2.0.0", app=self.app)
        self.url = reverse("admin:core_app_renew_certificate", args=[self.app.pk])

    def test_page_shows_current_certificate(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Serial number")

    def test_renewal_with_same_key_keeps_releases(self):
        self.client.force_login(self.admin)
        renewed = _cert(self.key, 2)
        response = self.client.post(self.url, {"certificate": renewed})
        self.assertRedirects(response, reverse("admin:core_app_change", args=[self.app.pk]))
        self.app.refresh_from_db()
        self.assertEqual(self.app.certificate, renewed.strip())
        self.assertEqual(self.app.releases.count(), 2)

    def test_renewal_with_different_key_is_refused(self):
        self.client.force_login(self.admin)
        original = self.app.certificate
        response = self.client.post(self.url, {"certificate": _cert(self.other_key, 2)})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "different public key")
        self.app.refresh_from_db()
        self.assertEqual(self.app.certificate, original)
        self.assertEqual(self.app.releases.count(), 2)

    def test_renewal_for_another_app_id_is_refused(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {"certificate": _cert(self.key, 2, cn="other")})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "does not match cert CN")
        self.app.refresh_from_db()
        self.assertEqual(self.app.releases.count(), 2)

    def test_change_page_shows_expiry_with_renewal_link(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:core_app_change", args=[self.app.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.url)
        self.assertContains(response, "Certificate expires")

    def test_app_list_highlights_certificates_close_to_expiry(self):
        App.objects.create(id="soon", certificate=_cert(self.key, 3, cn="soon", days=20), owner=self.owner)
        App.objects.create(id="placeholder", certificate="urn:uuid:0000", owner=self.owner)
        admin = site._registry[App]
        self.assertIn("certificate-expiry-warning", admin.certificate_expiry(App.objects.get(id="soon")))
        self.assertNotIn("certificate-expiry-warning", str(admin.certificate_expiry(self.app)))
        self.assertEqual(admin.certificate_expiry(App.objects.get(id="placeholder")), "-")

    def test_app_list_filters_certificates_by_expiry(self):
        App.objects.create(id="soon", certificate=_cert(self.key, 3, cn="soon", days=20), owner=self.owner)
        App.objects.create(id="gone", certificate=_cert(self.key, 4, cn="gone", days=-1), owner=self.owner)
        self.client.force_login(self.admin)
        changelist = reverse("admin:core_app_changelist")
        soon = self.client.get(changelist, {"certificate_expiry": "soon"}).context["cl"].queryset
        expired = self.client.get(changelist, {"certificate_expiry": "expired"}).context["cl"].queryset
        self.assertEqual(sorted(soon.values_list("id", flat=True)), ["soon"])
        self.assertEqual(sorted(expired.values_list("id", flat=True)), ["gone"])

    def test_non_staff_cannot_open_the_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response["Location"])

    def test_certificate_is_read_only_on_the_change_page(self):
        request = RequestFactory().get("/")
        request.user = self.admin
        self.assertIn("certificate", site._registry[App].get_readonly_fields(request, self.app))
        self.assertNotIn("certificate", site._registry[App].get_readonly_fields(request, None))
