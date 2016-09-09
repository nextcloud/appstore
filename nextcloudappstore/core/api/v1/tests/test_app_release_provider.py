from unittest.mock import Mock, MagicMock

from django.test import TestCase
from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor
from nextcloudappstore.core.api.v1.release.provider import \
    AppReleaseProvider, \
    InvalidAppDirectoryException
from nextcloudappstore.core.facades import read_relative_file, \
    resolve_file_relative_path
from pymple import Container


class FakeDownload:
    filename = resolve_file_relative_path(__file__,
                                          'data/infoxmls/minimal.xml')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ImporterTest(TestCase):
    def setUp(self):
        self.container = Container()

    def test_valid_checksum(self):
        xml = read_relative_file(__file__, 'data/infoxmls/minimal.xml')
        downloader = self.container.resolve(AppReleaseDownloader)
        downloader.get_archive = MagicMock(return_value=FakeDownload())
        extractor = self.container.resolve(GunZipAppMetadataExtractor)
        extractor.extract_app_metadata = MagicMock(return_value=(xml, 'news'))
        provider = self.container.resolve(AppReleaseProvider)

        info, checksum = provider.get_release_info('http://google.com')
        self.assertEqual(
            '306a81a5db301ed944886526a9303e8d5a670dcea7346cabb4e9c0815a4e218f'
            '2b1aaf8bc72a4d0ba89872bb0f0c60f53b42090c2ddfd383f65b79bcd8954110',
            checksum)

    def test_invalid_app_id(self):
        xml = read_relative_file(__file__, 'data/infoxmls/minimal.xml')
        downloader = self.container.resolve(AppReleaseDownloader)
        downloader.get_archive = MagicMock(return_value=FakeDownload())
        extractor = self.container.resolve(GunZipAppMetadataExtractor)
        extractor.extract_app_metadata = MagicMock(return_value=(xml, 'new'))
        provider = self.container.resolve(AppReleaseProvider)

        with self.assertRaises(InvalidAppDirectoryException):
            provider.get_release_info('http://google.com')
