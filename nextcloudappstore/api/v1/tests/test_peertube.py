"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.test import TestCase

from nextcloudappstore.api.v1.release.peertube import (
    InvalidPeerTubeUrl,
    peertube_embed_url,
)


class PeerTubeEmbedUrlTest(TestCase):
    def test_short_watch_url(self):
        self.assertEqual(
            peertube_embed_url("https://peertube.tv/w/dMWVlMwd9ecp5UVAOUhTDt"),
            "https://peertube.tv/videos/embed/dMWVlMwd9ecp5UVAOUhTDt",
        )

    def test_watch_url(self):
        self.assertEqual(
            peertube_embed_url("https://peertube.tv/videos/watch/TpUpEIu3PkYqljmQw7T0jR"),
            "https://peertube.tv/videos/embed/TpUpEIu3PkYqljmQw7T0jR",
        )

    def test_embed_url_passthrough(self):
        url = "https://peertube.tv/videos/embed/TpUpEIu3PkYqljmQw7T0jR"
        self.assertEqual(peertube_embed_url(url), url)

    def test_rejects_non_peertube_path(self):
        with self.assertRaises(InvalidPeerTubeUrl) as ctx:
            peertube_embed_url("https://peertube.tv/about")
        self.assertIn("/w/", str(ctx.exception.detail[0]))
