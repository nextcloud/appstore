"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.test import tag

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class ProfileTokenTest(BaseStoreTest):
    fixtures = [
        "admin.json",
    ]

    def test_update_token(self):
        self.login()
        self.go_to("user:account-api-token")

        btn_selector = '#api-token-regen-form input[type="submit"]:not([disabled])'
        token = self._update_token(btn_selector)

        def assert_new_token(el):
            self.assertEqual(40, len(token))
            new_token = self.by_id("token").text.strip()

            self.assertEqual(len(token), len(new_token))
            self.assertNotEqual(token, new_token)

        self.wait_for(btn_selector, assert_new_token)

    def _update_token(self, btn_selector) -> str:
        def click_regen(el):
            token = self.by_id("token")
            text = token.text
            self.by_css(btn_selector).click()
            return text.strip()

        return self.wait_for(btn_selector, click_regen)
