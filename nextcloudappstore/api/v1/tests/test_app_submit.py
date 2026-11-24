"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest.mock import patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from django.test import override_settings
from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.github import AppCertificateExistsError
from nextcloudappstore.core.models import App


def _make_csr(cn: str) -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)]))
        .sign(key, hashes.SHA256())
    )
    return csr.public_bytes(serialization.Encoding.PEM).decode()


class AppSubmitTest(ApiTest):
    create_url = reverse("api:v1:app-submit")

    def setUp(self):
        super().setUp()
        self._csr = _make_csr("news")
        self._payload = {
            "app_id": "news",
            "repository": "https://github.com/example/news",
            "csr": self._csr,
        }

    @override_settings(
        GITHUB_API_TOKEN="test-token",
        GITHUB_APP_CERTIFICATE_REPO="nextcloud/app-certificate-requests",
        GITHUB_DCO_EMAIL="dco@nextcloud.com",
    )
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_creates_pr(self, create_pr):
        create_pr.return_value = "https://github.com/nextcloud/app-certificate-requests/pull/1"
        self._login()
        response = self.api_client.post(self.create_url, data=self._payload, format="json")
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            "https://github.com/nextcloud/app-certificate-requests/pull/1",
            response.json()["pullRequestUrl"],
        )
        create_pr.assert_called_once()
        args = create_pr.call_args
        self.assertEqual("nextcloud/app-certificate-requests", args.args[1])
        self.assertEqual("news", args.args[2])
        self.assertEqual(self._csr.strip(), args.args[3])
        self.assertEqual("https://github.com/example/news", args.args[4])
        self.assertEqual("test", args.args[5])
        self.assertEqual("dco@nextcloud.com", args.args[6])

    @override_settings(GITHUB_API_TOKEN="test-token")
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_rejects_existing_certificate(self, create_pr):
        create_pr.side_effect = AppCertificateExistsError("news")
        self._login()
        response = self.api_client.post(self.create_url, data=self._payload, format="json")
        self.assertEqual(400, response.status_code)

    @override_settings(GITHUB_API_TOKEN="test-token")
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_rejects_registered_app(self, create_pr):
        App.objects.create(id="news", owner=self.user)
        self._login()
        response = self.api_client.post(self.create_url, data=self._payload, format="json")
        self.assertEqual(400, response.status_code)
        create_pr.assert_not_called()

    @override_settings(GITHUB_API_TOKEN="test-token")
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_rejects_csr_cn_mismatch(self, create_pr):
        payload = dict(self._payload)
        payload["csr"] = _make_csr("other")
        self._login()
        response = self.api_client.post(self.create_url, data=payload, format="json")
        self.assertEqual(400, response.status_code)
        create_pr.assert_not_called()

    @override_settings(GITHUB_API_TOKEN="test-token")
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_rejects_long_app_id(self, create_pr):
        payload = {
            "app_id": "a" * 33,
            "repository": "https://github.com/example/news",
            "csr": _make_csr("a" * 33),
        }
        self._login()
        response = self.api_client.post(self.create_url, data=payload, format="json")
        self.assertEqual(400, response.status_code)
        create_pr.assert_not_called()

    def test_submit_unconfigured_is_server_error(self):
        self._login()
        response = self.api_client.post(self.create_url, data=self._payload, format="json")
        self.assertEqual(500, response.status_code)
