"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest.mock import patch

from django.urls import reverse
from django.test import override_settings

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.github import AppCertificateExistsError


class AppSubmitTest(ApiTest):
    create_url = reverse("api:v1:app-submit")
    _csr = (
        "-----BEGIN CERTIFICATE REQUEST-----\n"
        "MIIB\n"
        "-----END CERTIFICATE REQUEST-----"
    )
    _payload = {
        "app_id": "news",
        "repository": "https://github.com/example/news",
        "csr": _csr,
    }

    @override_settings(GITHUB_API_TOKEN="test-token", GITHUB_APP_CERTIFICATE_REPO="nextcloud/app-certificate-requests")
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
        self.assertEqual(self._csr, args.args[3])
        self.assertEqual("https://github.com/example/news", args.args[4])
        self.assertEqual("test", args.args[5])

    @override_settings(GITHUB_API_TOKEN="test-token")
    @patch("nextcloudappstore.api.v1.views.create_app_certificate_request_pr")
    def test_submit_rejects_existing_app(self, create_pr):
        create_pr.side_effect = AppCertificateExistsError("news")
        self._login()
        response = self.api_client.post(self.create_url, data=self._payload, format="json")
        self.assertEqual(400, response.status_code)
