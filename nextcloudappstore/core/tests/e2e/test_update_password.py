from django.test import tag

from nextcloudappstore.core.tests.e2e import TEST_PASSWORD  # , TEST_USER
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag('e2e')
class UpdatePasswordTest(BaseStoreTest):
    def test_update_pass(self):
        self.login()
        self.go_to('user:account-password')

        old = self.by_id('id_oldpassword')
        old.clear()
        old.send_keys(TEST_PASSWORD)

        pass1 = self.by_id('id_password1')
        pass1.clear()
        pass1.send_keys('thisisatest')

        pass2 = self.by_id('id_password2')
        pass2.clear()
        pass2.send_keys('thisisatest')
        pass2.submit()

        # TODO FIXME false positive test
        # self.assertTrue(self.by_css('.alert-success').is_displayed())

        # self.login(TEST_USER, 'thisisatest')

        # self.assertTrue(
        #     self.findNavigationLink('account_logout').is_displayed())
