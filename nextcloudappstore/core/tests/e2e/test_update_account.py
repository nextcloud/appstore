from django.test import tag

from nextcloudappstore.core.tests.e2e import TEST_PASSWORD
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class UpdateAccountTest(BaseStoreTest):
    def test_update_account(self):
        self.login()
        self.go_to("user:account")

        first = self.by_id("id_first_name")
        first.clear()
        first.send_keys("change")
        last = self.by_id("id_last_name")
        last.clear()
        last.send_keys("me")

        mail = self.by_id("id_email")
        mail.clear()
        mail.send_keys("change@me.com")

        passwd = self.by_id("id_passwd")
        passwd.clear()
        passwd.send_keys(TEST_PASSWORD)

        passwd.submit()

        self.assertTrue(self.by_css(".alert-success").is_displayed())

        self.go_to("user:account")

        first = self.by_id("id_first_name").get_attribute("value")
        last = self.by_id("id_last_name").get_attribute("value")
        mail = self.by_id("id_email").get_attribute("value")

        self.assertEqual("change", first)
        self.assertEqual("me", last)
        self.assertEqual("change@me.com", mail)
