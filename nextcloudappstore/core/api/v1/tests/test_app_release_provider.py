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

        info = provider.get_release_info('http://google.com')
        self.assertEqual(
            'f44ff51ce0cd12e37367af5cb02ccab0e5fc29625b1b013665b833435'
            '0bc8836', info['app']['release']['checksum'])

    def test_invalid_app_id(self):
        xml = read_relative_file(__file__, 'data/infoxmls/minimal.xml')
        downloader = self.container.resolve(AppReleaseDownloader)
        downloader.get_archive = MagicMock(return_value=FakeDownload())
        extractor = self.container.resolve(GunZipAppMetadataExtractor)
        extractor.extract_app_metadata = MagicMock(return_value=(xml, 'new'))
        provider = self.container.resolve(AppReleaseProvider)

        with self.assertRaises(InvalidAppDirectoryException):
            provider.get_release_info('http://google.com')
