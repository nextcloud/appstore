import pem
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, verify, X509, \
    X509Store, X509StoreContext
from django.conf import settings  # type: ignore
from rest_framework.exceptions import APIException


class CertificateConfiguration:
    def __init__(self) -> None:
        self.validate_certs = settings.VALIDATE_CERTIFICATES
        self.digest = settings.CERTIFICATE_DIGEST


class InvalidSignatureException(APIException):
    pass


class InvalidCertificateException(APIException):
    pass


class CertificateValidator:
    """
    See https://pyopenssl.readthedocs.io/en/stable/api/crypto.html#signing
    -and-verifying-signatures
    """

    def __init__(self, config: CertificateConfiguration) -> None:
        self.config = config

    def validate_signature(self, certificate: str, signature: str,
                           data: str) -> None:
        """
        Tests if a value is a valid certificate using SHA512
        Logs an error if self.config.validate_certs is False
        :param certificate: the certificate to use
        :param signature: the signature string to test
        :param data: the SHA512 value (e.g. archive SHA512 checksum)
        :raises: InvalidSignatureException if the signature is invalid
        :return: None
        """
        cert = self._to_cert(certificate)
        try:
            result = verify(cert, signature.encode(), data.encode(),
                            self.config.digest)
            if result is not None:
                raise InvalidSignatureException('Signature is invalid')
        except Exception as e:
            raise InvalidSignatureException(e)

    def validate_certificate(self, certificate: str, chain: str,
                             crl: str) -> None:
        """
        Tests if a certificate has been signed by the chain, is not revoked
        and has not yet been expired. Logs an error if
        self.config.validate_certs is False
        :param certificate: the certificate to test
        :param chain: the certificate chain file content
        :param crl: the certificate revocation list file content
        :raises: InvalidCertificateException if the certificate is invalid
        :return: None
        """
        # root and intermediary certificate need to be split
        cas = pem.parse(chain.encode())
        store = X509Store()
        for ca in cas:
            store.add_cert(self._to_cert(str(ca)))

        cert = self._to_cert(certificate)
        ctx = X509StoreContext(store, cert)
        try:
            result = ctx.verify_certificate()
            if result is not None:
                raise InvalidCertificateException('Certificate is invalid')
        except Exception as e:
            raise InvalidCertificateException(e)

    def get_cn(self, certificate: str) -> str:
        """
        Extracts the CN from a certificate and removes the leading
        slash, e.g. /news should return news
        :param certificate: certificate
        :return: the certificate's subject without the leading slash
        """
        cert = self._to_cert(certificate)
        return cert.get_subject().CN[1:]

    def _to_cert(self, certificate: str) -> X509:
        return load_certificate(FILETYPE_PEM, certificate.encode())
