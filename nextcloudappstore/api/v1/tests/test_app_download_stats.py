"""
SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.core.models import App, AppRelease

GITHUB_URL = "https://github.com/nextcloud-releases/spreed/releases/download/v29.0.0/spreed.tar.gz"
OTHER_URL = "https://example.com/spreed-28.0.0.tar.gz"

MOCK_GH_RELEASES = [
    {
        "tag_name": "v29.0.0",
        "assets": [{"name": "spreed.tar.gz", "download_count": 13832}],
    }
]


class AppDownloadStatsTest(ApiTest):
    def setUp(self):
        super().setUp()
        self.app = App.objects.create(id="spreed", owner=self.user)
        AppRelease.objects.create(
            app=self.app,
            version="29.0.0",
            download=GITHUB_URL,
            platform_version_spec=">=30.0.0",
        )
        AppRelease.objects.create(
            app=self.app,
            version="28.0.0",
            download=OTHER_URL,
            platform_version_spec=">=29.0.0",
        )

    def _url(self, pk="spreed"):
        return reverse("api:v1:app-download-stats", kwargs={"pk": pk})

    @patch("nextcloudappstore.api.v1.views.GitHubClient")
    def test_owner_sees_counts(self, MockClient):
        MockClient.return_value.get_releases.return_value = MOCK_GH_RELEASES
        self._login_token()
        response = self.api_client.get(self._url())
        self.assertEqual(200, response.status_code)
        by_version = {r["version"]: r for r in response.data}
        self.assertEqual(13832, by_version["29.0.0"]["download_count"])
        self.assertIsNone(by_version["28.0.0"]["download_count"])

    @patch("nextcloudappstore.api.v1.views.GitHubClient")
    def test_co_maintainer_sees_counts(self, MockClient):
        MockClient.return_value.get_releases.return_value = MOCK_GH_RELEASES
        other = get_user_model().objects.create_user(username="other", password="other", email="other@test.com")
        self.app.co_maintainers.add(other)
        self._login("other", "other")
        response = self.api_client.get(self._url())
        self.assertEqual(200, response.status_code)

    def test_unauthenticated_returns_401(self):
        response = self.api_client.get(self._url())
        self.assertEqual(401, response.status_code)

    def test_non_maintainer_returns_403(self):
        stranger = get_user_model().objects.create_user(
            username="stranger", password="stranger", email="stranger@test.com"
        )
        App.objects.create(id="other_app", owner=stranger)
        self._login_token()
        response = self.api_client.get(reverse("api:v1:app-download-stats", kwargs={"pk": "other_app"}))
        self.assertEqual(403, response.status_code)

    def test_unknown_app_returns_404(self):
        self._login_token()
        response = self.api_client.get(self._url("nonexistent"))
        self.assertEqual(404, response.status_code)

    @patch("nextcloudappstore.api.v1.views.GitHubClient")
    def test_github_api_error_yields_null_count(self, MockClient):
        import requests as req

        MockClient.return_value.get_releases.side_effect = req.RequestException("rate limited")
        self._login_token()
        response = self.api_client.get(self._url())
        self.assertEqual(200, response.status_code)
        for entry in response.data:
            self.assertIsNone(entry["download_count"])

    @patch("nextcloudappstore.api.v1.views.GitHubClient")
    def test_response_shape(self, MockClient):
        MockClient.return_value.get_releases.return_value = MOCK_GH_RELEASES
        self._login_token()
        response = self.api_client.get(self._url())
        self.assertEqual(200, response.status_code)
        for entry in response.data:
            self.assertIn("version", entry)
            self.assertIn("is_nightly", entry)
            self.assertIn("download", entry)
            self.assertIn("download_count", entry)
