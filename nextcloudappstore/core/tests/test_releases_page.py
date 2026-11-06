"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from nextcloudappstore.core.models import App, AppRelease, NextcloudRelease


class ReleasesPageTest(TestCase):
    def setUp(self):
        cache.clear()
        for version in ("30.0.0", "31.0.0", "32.0.0", "33.0.0"):
            NextcloudRelease.objects.create(version=version)
        self.app = App.objects.create(id="news", owner=User.objects.create(username="owner"))
        for version, spec, is_nightly in (
            ("1.0.0", ">=30.0.0,<33.0.0", False),
            ("0.9.0", ">=30.0.0,<32.0.0", False),
            ("1.1.0-beta.1", ">=30.0.0", False),
            ("1.1.0", ">=33.0.0", True),
        ):
            AppRelease.objects.create(
                app=self.app,
                version=version,
                platform_version_spec=spec,
                is_nightly=is_nightly,
                download=f"https://example.com/news-{version}.tar.gz",
            )

    def _get(self, **params):
        response = self.client.get(reverse("app-releases", kwargs={"id": self.app.id}), params)
        self.assertEqual(200, response.status_code)
        return response

    def _versions(self, response):
        return [release.version for release in response.context["releases"]]

    def test_shows_newest_platform_version_by_default(self):
        response = self._get()
        self.assertEqual("33", response.context["selected_platform"])
        self.assertEqual(["1.1.0", "1.1.0-beta.1"], self._versions(response))

    def test_lists_stable_before_unstable_releases(self):
        response = self._get(platform="31")
        self.assertEqual("31", response.context["selected_platform"])
        self.assertEqual(["1.0.0", "0.9.0", "1.1.0-beta.1"], self._versions(response))

    def test_falls_back_to_newest_for_unknown_platform_version(self):
        self.assertEqual("33", self._get(platform="99").context["selected_platform"])

    def test_offers_only_platform_versions_with_releases(self):
        NextcloudRelease.objects.create(version="29.0.0")
        self.assertEqual(["33", "32", "31", "30"], self._get().context["platform_versions"])

    def test_renders_one_download_per_release(self):
        response = self._get(platform="31")
        for version in ("1.0.0", "0.9.0", "1.1.0-beta.1"):
            self.assertContains(response, f'href="https://example.com/news-{version}.tar.gz"', count=1)
        self.assertContains(response, "btn-danger release-download", count=1)
        self.assertContains(response, "btn-primary release-download", count=2)
