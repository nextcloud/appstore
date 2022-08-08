import os

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest

from django.test import tag


@tag('e2e')
class UserRegisterTest(BaseStoreTest):
    def test_register(self):
        self.go_to('account_signup')
        self.by_id('id_first_name').send_keys('john')
        self.by_id('id_last_name').send_keys('doe')
        self.by_id('id_username').send_keys('johndoe')
        self.by_id('id_email').send_keys('john@doe.com')
        self.by_id('id_captcha_1').send_keys('PASSED')
        self.by_id('id_password1').send_keys('oalx77rkdf')
        self.by_id('id_password2').send_keys('oalx77rkdf')

        with self.settings(ACCOUNT_EMAIL_VERIFICATION='optional'):
            self.by_css('.auth-form button[type="submit"]').click()

            logout_link = self.findNavigationLink('account_logout')
            self.assertOnPage('home')

            logout_link.click()

            login_link = self.findNavigationLink('account_login')
            login_link.click()

            self.by_id('id_login').send_keys('johndoe')
            self.by_id('id_password').send_keys('oalx77rkdf')
            self.by_css('.auth-form button[type="submit"]').click()
            self.assertOnPage('home')
