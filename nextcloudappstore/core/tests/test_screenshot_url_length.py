"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from base64 import urlsafe_b64encode
from math import ceil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from nextcloudappstore.api.v1.release.importer import ScreenshotsImporter
from nextcloudappstore.core.models import App, Screenshot

# info.xsd restricts `secure-url`, which is what a <screenshot> is, to 256 characters.
MAX_SOURCE_URL_LENGTH = 256


def proxy_url(url: str) -> str:
    """The same transformation ScreenshotsImporter and migration 0037 apply."""
    return f"{settings.USERCONTENT_PROXY_URL}/{urlsafe_b64encode(url.encode()).decode()}"


def source_url_of_length(length: int) -> str:
    prefix = "https://example.com/"
    return prefix + "a" * (length - len(prefix))


class ScreenshotUrlLengthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="hi")
        self.app = App.objects.create(id="news", owner=self.user)

    def _max_length(self):
        return Screenshot._meta.get_field("url").max_length

    def test_the_column_fits_the_longest_url_the_schema_allows(self):
        """Guards the arithmetic rather than one example.

        Proxying base64-encodes the source into the path, which costs 4 bytes per 3, so the
        column has to hold len(base) + 1 + 4 * ceil(256 / 3). This fails if someone shrinks the
        column again or lengthens USERCONTENT_PROXY_URL.
        """
        widest = len(settings.USERCONTENT_PROXY_URL) + 1 + 4 * ceil(MAX_SOURCE_URL_LENGTH / 3)

        self.assertLessEqual(widest, self._max_length())

    def test_a_source_url_of_162_characters_used_to_be_the_ceiling(self):
        """The regression this guards: at max_length=256 anything longer overflowed.

        Kept as an explicit boundary so the reason for the widening survives in the test suite.
        """
        self.assertGreater(len(proxy_url(source_url_of_length(163))), 256)
        self.assertLessEqual(len(proxy_url(source_url_of_length(162))), 256)

    def test_a_maximum_length_source_url_round_trips_through_the_database(self):
        url = proxy_url(source_url_of_length(MAX_SOURCE_URL_LENGTH))

        screenshot = Screenshot.objects.create(url=url, ordering=1, app=self.app)
        screenshot.refresh_from_db()

        self.assertEqual(url, screenshot.url)

    def test_the_importer_stores_a_maximum_length_source_url(self):
        source = source_url_of_length(MAX_SOURCE_URL_LENGTH)
        importer = ScreenshotsImporter()

        importer.import_data(
            "screenshots",
            [{"screenshot": {"url": source, "ordering": 1, "small_thumbnail": ""}}],
            self.app,
        )

        stored = self.app.screenshots.get()
        self.assertEqual(proxy_url(source), stored.url)
