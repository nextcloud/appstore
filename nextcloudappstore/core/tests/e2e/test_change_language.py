"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.test import tag
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from nextcloudappstore.core.tests.e2e import SELENIUM_WAIT_SEC
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class ChangeLanguageTest(BaseStoreTest):
    def test_change_lang(self):
        self.login()
        self.go_to("user:account-change-language")

        elem = self.by_id("language")
        lang = Select(elem)
        lang.select_by_value("de")
        elem.submit()

        WebDriverWait(self.selenium, SELENIUM_WAIT_SEC).until(staleness_of(elem))
        account_link = self.findNavigationLink("user:account")
        self.assertEqual("person\nKonto", account_link.text)
