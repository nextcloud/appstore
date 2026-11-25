"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from nextcloudappstore.certificate.validator import has_same_public_key
from nextcloudappstore.core.models import App, AppRelease


class CertDeleteReleasesTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create(username="user", password="pass")
        self.app = App.objects.create(name="App", certificate="CERT1", owner=self.owner)
        self.rel1 = AppRelease.objects.create(version="1.0.0", app=self.app)
        self.rel2 = AppRelease.objects.create(version="2.0.0", app=self.app)
        self.rel3 = AppRelease.objects.create(version="3.0.0", app=self.app)
        self.rel4 = AppRelease.objects.create(version="4.0.0", app=self.app)

    def test_cert_has_changed(self):
        self.assertEqual(self.app.releases.count(), 4)
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "CERT2"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 0)

    def test_ignore_carriage_return(self):
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "CER\rT1"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 5)

    def test_ignore_start_end_spaces(self):
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "\n\nCER\rT1\n\n"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 5)


def _key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _cert(key, serial: int) -> str:
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "app")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(serial)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode()


class CertRenewalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.key = _key()
        cls.other_key = _key()

    def setUp(self):
        self.owner = User.objects.create(username="user", password="pass")
        self.app = App.objects.create(name="App", certificate=_cert(self.key, 1), owner=self.owner)
        AppRelease.objects.create(version="1.0.0", app=self.app)
        AppRelease.objects.create(version="2.0.0", app=self.app)

    def test_renewed_cert_with_same_key_keeps_releases(self):
        self.app.certificate = _cert(self.key, 2)
        self.app.save()
        self.assertEqual(self.app.releases.count(), 2)

    def test_renewed_cert_with_crlf_keeps_releases(self):
        self.app.certificate = _cert(self.key, 2).replace("\n", "\r\n")
        self.app.save()
        self.assertEqual(self.app.releases.count(), 2)

    def test_cert_with_new_key_deletes_releases(self):
        self.app.certificate = _cert(self.other_key, 2)
        self.app.save()
        self.assertEqual(self.app.releases.count(), 0)

    def test_unparseable_new_cert_deletes_releases(self):
        self.app.certificate = "not a certificate"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 0)


class HasSamePublicKeyTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.key = _key()
        cls.other_key = _key()

    def test_same_key_different_serial(self):
        self.assertTrue(has_same_public_key(_cert(self.key, 1), _cert(self.key, 2)))

    def test_same_key_crlf_and_whitespace(self):
        crlf = "\n" + _cert(self.key, 2).replace("\n", "\r\n") + "  \n"
        self.assertTrue(has_same_public_key(_cert(self.key, 1), crlf))

    def test_different_key(self):
        self.assertFalse(has_same_public_key(_cert(self.key, 1), _cert(self.other_key, 1)))

    def test_unparseable(self):
        cert = _cert(self.key, 1)
        for bad in ("", "not a certificate"):
            with self.subTest(bad=bad):
                self.assertFalse(has_same_public_key(cert, bad))
                self.assertFalse(has_same_public_key(bad, cert))
