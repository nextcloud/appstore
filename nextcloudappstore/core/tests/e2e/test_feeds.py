"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import requests
from django.test import tag

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class FeedTest(BaseStoreTest):
    fixtures = [
        "categories.json",
        "databases.json",
        "licenses.json",
        "nextcloudreleases.json",
        "apps.json",
        "admin.json",
    ]

    def test_rss_all(self):
        self.go_to("home")

        rss_url = self.by_css('link[type="application/rss+xml"]')

        response = requests.get(rss_url.get_attribute("href"))
        result = response.text

        self.assertEqual(200, response.status_code)
        self.assertTrue(len(result) > 0)
        self.assertIn("News (10.1.0)", result)

    def test_atom_all(self):
        self.go_to("home")

        rss_url = self.by_css('link[type="application/atom+xml"]')
        response = requests.get(rss_url.get_attribute("href"))
        result = response.text

        self.assertEqual(200, response.status_code)
        self.assertTrue(len(result) > 0)
        self.assertIn("News (10.1.0)", result)
