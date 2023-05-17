from django.test import TestCase
from pymple import Container

from nextcloudappstore.certificate.validator import (
    CertificateAppIdMismatchException,
    CertificateConfiguration,
    CertificateValidator,
    InvalidCertificateException,
    InvalidSignatureException,
)
from nextcloudappstore.core.facades import (
    read_relative_file,
    resolve_file_relative_path,
)


class ValidatorTest(TestCase):
    def setUp(self) -> None:
        self.container = Container()
        self.validator = self.container.resolve(CertificateValidator)
        self.config = self.container.resolve(CertificateConfiguration)

    def test_get_cn(self) -> None:
        cert = self._read_cert("app.crt")
        self.assertEqual("folderplayer", self.validator.get_cn(cert))

    def test_validate_app_id(self) -> None:
        cert = self._read_cert("app.crt")
        self.validator.validate_app_id(cert, "folderplayer")

    def test_validate_app_id_invalid(self) -> None:
        cert = self._read_cert("app.crt")
        with self.assertRaises(CertificateAppIdMismatchException):
            self.validator.validate_app_id(cert, "/folderplayer")

    def test_validate_cert_signed(self) -> None:
        cert = self._read_cert("app.crt")
        chain = self._read_cert("owncloud.crt")
        self.validator.validate_certificate(cert, chain)

    def test_validate_old_cert_signed(self) -> None:
        cert = self._read_cert("news-old.crt")
        chain = self._read_cert("owncloud.crt")
        self.validator.validate_certificate(cert, chain)

    def test_validate_cert_not_signed(self) -> None:
        cert = self._read_cert("app.crt")
        chain = self._read_cert("imaginary.chain")
        with self.assertRaises(InvalidCertificateException):
            self.validator.validate_certificate(cert, chain)

    def test_signature(self) -> None:
        cert = self._read_cert("news-old.crt")
        sign = self._read_cert("news-old-minimal.sig")
        checksum = self._read_bin_file("data/archives/minimal.tar.gz")
        self.validator.validate_signature(cert, sign, checksum)

    def test_app_id_signature(self) -> None:
        cert = self._read_cert("news-old.crt")
        sign = self._read_cert("news-old-app-id.sig")
        self.validator.validate_signature(cert, sign, "news".encode())

    def test_bad_signature(self) -> None:
        cert = self._read_cert("news-old.crt")
        sign = self._read_cert("bad-news-old-minimal.sig")
        checksum = self._read_bin_file("data/archives/minimal.tar.gz")
        with self.assertRaises(InvalidSignatureException):
            self.validator.validate_signature(cert, sign, checksum)

    def test_validate_cert_signed_not_on_crl(self) -> None:
        cert = self._read_cert("imaginary-revoked1.crt")
        chain = self._read_cert("imaginary.chain")
        crl = self._read_cert("empty.crl")
        self.validator.validate_certificate(cert, chain, crl)

    def test_validate_crl(self) -> None:
        cert = self._read_cert("imaginary-valid.crt")
        chain = self._read_cert("imaginary.chain")
        crl = self._read_cert("imaginary.crl")
        self.validator.validate_certificate(cert, chain, crl)

    def test_validate_crl_revoked1(self) -> None:
        cert = self._read_cert("imaginary-revoked1.crt")
        chain = self._read_cert("imaginary.chain")
        crl = self._read_cert("imaginary.crl")
        with self.assertRaises(InvalidCertificateException):
            self.validator.validate_certificate(cert, chain, crl)

    def test_validate_crl_revoked2(self) -> None:
        cert = self._read_cert("imaginary-revoked2.crt")
        chain = self._read_cert("imaginary.chain")
        crl = self._read_cert("imaginary.crl")
        with self.assertRaises(InvalidCertificateException):
            self.validator.validate_certificate(cert, chain, crl)

    def _read_cert(self, file: str) -> str:
        return read_relative_file(__file__, "data/certificates/%s" % file)

    def _read_bin_file(self, rel_path: str) -> bytes:
        target_path = resolve_file_relative_path(__file__, rel_path)
        with open(target_path, "rb") as f:
            return f.read()
