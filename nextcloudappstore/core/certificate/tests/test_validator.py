from django.test import TestCase
from pymple import Container

from nextcloudappstore.core.certificate.validator import CertificateValidator, \
    InvalidCertificateException
from nextcloudappstore.core.facades import read_relative_file


class ValidatorTest(TestCase):
    def setUp(self) -> None:
        self.container = Container()
        self.validator = self.container.resolve(CertificateValidator)

    def test_get_cn(self) -> None:
        cert = read_relative_file(__file__, 'data/certificates/app.crt')
        self.assertEqual('olderplayer', self.validator.get_cn(cert))

    def test_validate_cert_signed(self) -> None:
        cert = read_relative_file(__file__, 'data/certificates/app.crt')
        chain = read_relative_file(__file__, 'data/certificates/owncloud.crt')
        self.validator.validate_certificate(cert, chain, None)

    def test_validate_cert_crl(self) -> None:
        # TBD
        self.assertTrue(True)

    def test_validate_cert_not_signed(self) -> None:
        cert = read_relative_file(__file__, 'data/certificates/app.crt')
        chain = read_relative_file(__file__,
                                   'data/certificates/nextcloud.crt')
        with(self.assertRaises(InvalidCertificateException)):
            self.validator.validate_certificate(cert, chain, None)
