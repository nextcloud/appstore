from enum import Enum

from nextcloudappstore.core.tests.e2e import NEWS_ARCHIVE_URL, NEWS_SIGNATURE
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest
from nextcloudappstore.core.tests.e2e.facades import validate_email


class Rating(Enum):
    BAD = 'id_rating_0'
    OK = 'id_rating_1'
    GOOD = 'id_rating_2'


class UploadAppReleaseTest(BaseStoreTest):
    fixtures = [
        'categories.json',
        'databases.json',
        'licenses.json',
        'nextcloudreleases.json',
        'admin.json',
        'apps.json',
    ]

    def test_upload_invalid_url(self):
        self.login()
        self._upload_app('no url', 'sig')
        self.wait_for('.error-msg-download',
                      lambda el: self.assertTrue(el.is_displayed()))

    def test_upload(self):
        validate_email('admin', 'admin@admin.com')
        self.login('admin', 'admin')
        self._upload_app(NEWS_ARCHIVE_URL, NEWS_SIGNATURE)

        def check_app_version_page(el):
            self.go_to_app('news')
            a = self.by_css(
                '#downloads + table tr:first-child td:nth-child(2) a')

            self.assertEqual('11.0.5', a.text)
            self.assertEqual(NEWS_ARCHIVE_URL, a.get_attribute('href'))

        self.wait_for('.global-success-msg', check_app_version_page)

    def _upload_app(self, url, sig):
        self.go_to_app_upload()
        self.by_id('id_download').send_keys(url)
        self.by_id('id_signature').send_keys(sig)
        self.by_id('submit').click()
