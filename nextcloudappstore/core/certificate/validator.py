from django.conf import settings  # type: ignore
from OpenSSL.crypto import verify, X509, X509StoreContext, X509Store


class CertificateConfiguration:
    def __init__(self) -> None:
        self.validate_certs = settings.VALIDATE_CERTIFICATES


class CertificateValidator:
    """
    See https://pyopenssl.readthedocs.io/en/stable/api/crypto.html#signing
    -and-verifying-signatures
    """

    def __init__(self, config: CertificateConfiguration) -> None:
        self.config = config

    def is_valid_signature(self, certificate: str, signature: str,
                           data: str) -> bool:
        """
        Tests if a value is a valid certificate using SHA512
        Logs an error if self.config.validate_certs is False
        :param certificate: the certificate to use
        :param signature: the signature string to test
        :param data: the SHA512 value (e.g. archive SHA512 checksum)
        :return: True if valid or self.config.validate_certs is False
        """
        pass

    def is_valid_certificate(self, certificate: str, chain: str,
                             crl: str) -> bool:
        """
        Tests if a certificate has been signed by the chain, is not revoked
        and has not yet been expired. Logs an error if
        self.config.validate_certs is False
        :param certificate: the certificate to test
        :param chain: the certificate chain file content
        :param crl: the certificate revocation list file content
        :return: True if valid or self.config.validate_certs is False
        """
        pass

    def get_subject(self, certificate: str) -> str:
        """
        Extracts the subject from a certificate, e.g. /news
        :param certificate: certificate
        :return: the certificate's CN
        """
        pass
