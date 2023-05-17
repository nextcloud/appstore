from django.test import tag

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class UploadInvalidAppReleaseTest(BaseStoreTest):
    fixtures = [
        "categories.json",
        "databases.json",
        "licenses.json",
        "nextcloudreleases.json",
    ]

    def test_upload_invalid_url(self):
        self.login()
        with self.settings(VALIDATE_CERTIFICATES=False):
            self._upload_app("no url", "sig")
            self.wait_for(".error-msg-download", lambda el: self.assertTrue(el.is_displayed()))

    def _upload_app(self, url, sig):
        self.go_to_app_upload()
        self.by_id("id_download").send_keys(url)
        self.by_id("id_signature").send_keys(sig)
        self.by_id("submit").click()
