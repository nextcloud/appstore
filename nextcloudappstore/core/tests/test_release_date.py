"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime
import re

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from nextcloudappstore.api.v1.serializers import AppReleaseSerializer, AppSerializer
from nextcloudappstore.core.caching import apps_etag
from nextcloudappstore.core.models import App, AppRelease, NextcloudRelease


class ReleaseDateTest(TestCase):
    def setUp(self):
        NextcloudRelease.objects.create(version="9.1.1")
        self.user = User.objects.create(username="hi")
        self.app = App.objects.create(id="news", owner=self.user)
        self.release = AppRelease.objects.create(app=self.app, version="1.0.0", platform_version_spec=">=9.1.1")
        self.release_date = timezone.make_aware(datetime.datetime(2019, 3, 4, 12, 0))

    def _get_releases_page(self):
        response = self.client.get(reverse("app-releases", kwargs={"id": self.app.id}))
        self.assertEqual(200, response.status_code)
        # guards the two assertions below against passing because nothing rendered at all
        self.assertContains(response, self.release.version)
        return response

    def test_release_date_is_unset_by_default(self):
        self.assertIsNone(self.release.release_date)

    def test_releases_page_falls_back_to_the_upload_timestamp(self):
        self.assertNotContains(self._get_releases_page(), "2019")

    def test_releases_page_shows_the_release_date_when_set(self):
        self.release.release_date = self.release_date
        self.release.save()

        self.assertContains(self._get_releases_page(), "2019")

    def test_release_date_does_not_change_the_apps_etag(self):
        request = RequestFactory().get("/")
        before = apps_etag(request, "1.0.0")

        self.release.release_date = self.release_date
        self.release.save()

        self.assertEqual(before, apps_etag(request, "1.0.0"))

    def test_release_date_is_not_exposed_by_the_api(self):
        self.assertNotIn("release_date", AppReleaseSerializer().fields)


class IntegrationReleaseDateTest(TestCase):
    """Integrations never upload a release, so App.last_release keeps the value it was registered with."""

    def setUp(self):
        self.user = User.objects.create(username="hi")
        self.registered = timezone.now() - datetime.timedelta(days=6 * 365)
        self.app = App.objects.create(
            id="outlook", owner=self.user, is_integration=True, approved=True, last_release=self.registered
        )

    def _last_updated(self):
        response = self.client.get(reverse("app-detail", kwargs={"id": self.app.id}))
        self.assertEqual(200, response.status_code)
        match = re.search(r"Last updated</h2>\s*<p>(.*?)</p>", response.content.decode(), re.S)
        self.assertIsNotNone(match, "the detail page did not render a Last updated section")
        return match.group(1).strip()

    def test_release_date_is_unset_by_default(self):
        self.assertIsNone(self.app.release_date)

    def test_detail_page_falls_back_to_the_last_release(self):
        self.assertIn("years", self._last_updated())

    def test_detail_page_shows_the_release_date_when_set(self):
        self.app.release_date = timezone.now()
        self.app.save()

        self.assertNotIn("years", self._last_updated())

    def test_release_date_does_not_change_the_apps_etag(self):
        request = RequestFactory().get("/")
        before = apps_etag(request, "1.0.0")

        self.app.release_date = timezone.now()
        self.app.save()

        self.assertEqual(before, apps_etag(request, "1.0.0"))

    def test_release_date_is_not_exposed_by_the_api(self):
        self.assertNotIn("release_date", AppSerializer().fields)
