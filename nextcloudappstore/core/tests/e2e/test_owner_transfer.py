from django.test import tag
from django.urls import reverse

from nextcloudappstore.core.tests.e2e import NEWS_CERT
from nextcloudappstore.core.tests.e2e.app_dev_steps import AppDevSteps
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest
from nextcloudappstore.user.facades import verify_email


@tag('e2e')
class AppTransferTestTest(BaseStoreTest, AppDevSteps):
    fixtures = [
        'categories.json',
        'databases.json',
        'licenses.json',
        'nextcloudreleases.json',
        'admin.json',
        'apps.json',
    ]

    def test_transfer(self):
        # try to register locked app
        self.login()
        self.go_to_app_register()

        with self.settings(VALIDATE_CERTIFICATES=False):
            self.register_app(NEWS_CERT, 'signature')
            self.wait_for('.global-error-msg',
                          lambda el: self.assertTrue(el.is_displayed()))
        # unlock app
        self.logout()
        verify_email('admin', 'admin@admin.com')
        self.login('admin', 'admin')
        self.go_to('user:account-transfer-apps')
        news_transfer_url = reverse('user:account-transfer-app',
                                    kwargs={'pk': 'news'})
        self.by_css('form[action="%s"] button' % news_transfer_url).click()
        self.logout()

        # try to register unlocked app
        self.login()
        self.go_to_app_register()
        with self.settings(VALIDATE_CERTIFICATES=False):
            self.register_app(NEWS_CERT, 'signature')
            self.wait_for('.global-success-msg',
                          lambda el: self.assertTrue(el.is_displayed()))

        self.go_to('user:account-transfer-apps')
        el = self.by_css('form[action="%s"] button' % news_transfer_url)
        self.assertTrue(el.is_displayed())
