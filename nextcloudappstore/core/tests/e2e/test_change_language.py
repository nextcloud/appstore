from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest

from django.test import tag


@tag('e2e')
class ChangeLanguageTest(BaseStoreTest):
    def test_change_lang(self):
        self.login()
        self.go_to('user:account-change-language')

        elem = self.by_id('language')
        lang = Select(elem)
        lang.select_by_value('de')
        elem.submit()

        self.go_to('user:account-change-language')
        account_link = self.findNavigationLink('user:account')
        self.assertEqual('Konto', account_link.text)

