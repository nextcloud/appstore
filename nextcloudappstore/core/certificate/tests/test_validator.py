from django.test import TestCase
from pymple import Container

from nextcloudappstore.core.certificate.validator import CertificateValidator
from nextcloudappstore.core.facades import read_relative_file


class ValidatorTest(TestCase):
    def setUp(self) -> None:
        self.container = Container()
        self.validator = self.container.resolve(CertificateValidator)

    def test_get_cn(self) -> None:
        cert = read_relative_file(__file__, 'data/certificates/app.crt')
        self.assertEqual('olderplayer', self.validator.get_cn(cert))
