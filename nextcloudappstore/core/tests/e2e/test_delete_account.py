import time

from django.test import tag

from nextcloudappstore.core.tests.e2e.base import (
    TEST_EMAIL,
    TEST_PASSWORD,
    BaseStoreTest,
)


@tag("e2e")
class DeleteAccountTest(BaseStoreTest):
    def test_delete_account(self):
        self.login()
        self.go_to("user:account-deletion")

        # test non matching address
        self.by_id("id_email").clear()
        self.by_id("id_email").send_keys("livetest@localhos")
        self.by_id("id_passwd").send_keys(TEST_PASSWORD)
        self.by_id("id_email").submit()

        self.wait_for(".text-danger", lambda el: self.assertTrue(el.is_displayed()))

        # test valid address
        self.by_id("id_email").clear()
        self.by_id("id_email").send_keys(TEST_EMAIL)
        self.by_id("id_passwd").send_keys(TEST_PASSWORD)
        self.by_id("id_email").submit()

        time.sleep(3)
        self.assert_can_not_login()
