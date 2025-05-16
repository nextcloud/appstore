"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.test import tag

from nextcloudappstore.core.tests.e2e import (
    NEWS_ARCHIVE_SIGNATURE,
    NEWS_ARCHIVE_URL,
    NEWS_CERT,
)
from nextcloudappstore.core.tests.e2e.app_dev_steps import AppDevSteps
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class UploadAppReleaseTest(BaseStoreTest, AppDevSteps):
    fixtures = [
        "categories.json",
        "databases.json",
        "licenses.json",
        "nextcloudreleases.json",
        "admin.json",
    ]

    def test_upload(self):
        self.login()

        def check_app_version_page(el):
            self.go_to_app("news")
            a = self.by_css("#downloads + table tr:first-child td:nth-child(2) a")

            self.assertEqual("11.0.5", a.text)
            self.assertEqual(NEWS_ARCHIVE_URL, a.get_attribute("href"))

            self.by_css("#downloads + table tr:first-child td:last-child a").click()
            a = self.by_css(".release-download")
            self.assertEqual(NEWS_ARCHIVE_URL, a.get_attribute("href"))

        def upload_app(el):
            self._upload_app(NEWS_ARCHIVE_URL, NEWS_ARCHIVE_SIGNATURE)
            self.wait_for(".global-success-msg", check_app_version_page)

        with self.settings(VALIDATE_CERTIFICATES=True):
            self.register_app(NEWS_CERT, "test")

        # and run them for uploading the app archive
        self.wait_for(".global-success-msg", upload_app)

    def _upload_app(self, url, sig):
        self.go_to_app_upload()
        self.by_id("id_download").send_keys(url)
        self.by_id("id_signature").send_keys(sig)
        self.by_id("submit").click()
