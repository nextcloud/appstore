from django.test import tag

from nextcloudappstore.core.facades import (
    read_relative_file,
    resolve_file_relative_path,
)
from nextcloudappstore.core.models import App
from nextcloudappstore.core.tests.e2e import TEST_APP_SIG
from nextcloudappstore.core.tests.e2e.app_dev_steps import AppDevSteps
from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class AppRegistrationTest(BaseStoreTest, AppDevSteps):
    fixtures = [
        "categories.json",
        "databases.json",
        "licenses.json",
        "nextcloudreleases.json",
    ]

    def test_invalid_cert(self):
        self.login()

        def validate_error_msg(el):
            msg = (
                "Signature is invalid: [('rsa routines', "
                "'', 'wrong signature length'), "
                "('Provider routines', '', 'RSA lib')]"
            )
            self.assertTrue(el.is_displayed())
            self.assertEqual(msg, el.text.strip())

        with self.settings(
            VALIDATE_CERTIFICATES=True,
            NEXTCLOUD_CERTIFICATE_LOCATION=self.cert_path("ca.crt"),
            NEXTCLOUD_CRL_LOCATION=self.cert_path("ca.crl"),
        ):
            self.register_app(self.read_cert("app.crt"), "test")
            self.wait_for(".global-error-msg", validate_error_msg)

    def test_valid_cert(self):
        self.login()

        def validate_success_msg(el):
            self.assertTrue(el.is_displayed())
            app = App.objects.get(id="test")
            self.assertEqual("livetest", app.owner.username)

        with self.settings(
            VALIDATE_CERTIFICATES=True,
            NEXTCLOUD_CERTIFICATE_LOCATION=self.cert_path("ca.crt"),
            NEXTCLOUD_CRL_LOCATION=self.cert_path("ca.crl"),
        ):
            self.register_app(self.read_cert("app.crt"), TEST_APP_SIG)
            self.wait_for(".global-success-msg", validate_success_msg)

    def read_cert(self, name: str) -> str:
        return read_relative_file(__file__, f"data/{name}")

    def cert_path(self, name: str) -> str:
        return resolve_file_relative_path(__file__, f"data/{name}")
