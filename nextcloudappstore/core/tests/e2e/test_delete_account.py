from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


class DeleteAccountTest(BaseStoreTest):
    def test_delete_account(self):
        self.login()
        self.go_to('user:account-deletion')

        # test non matching address
        self.by_id('id_email').send_keys('livetest@localhos')
        self.by_id('id_email').submit()

        self.wait_for('.text-danger',
                      lambda el: self.assertTrue(el.is_displayed()))

        # test valid address
        self.by_id('id_email').clear()
        self.by_id('id_email').send_keys('livetest@localhost')
        self.by_id('id_email').submit()

        # check if not able to login anymore
        self.go_to_login()
        self.by_id('id_login').send_keys('livetest')
        self.by_id('id_password').send_keys('livetest')
        self.by_css('.auth-form button[type="submit"]').click()

        error = self.by_css('.auth-form .text-danger')
        self.assertTrue(error.is_displayed())
        self.assertOnPage('account_login')
