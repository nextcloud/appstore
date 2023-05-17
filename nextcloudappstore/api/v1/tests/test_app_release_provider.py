from unittest.mock import MagicMock

from django.test import TestCase
from pymple import Container

from nextcloudappstore.api.v1.release.downloader import AppReleaseDownloader
from nextcloudappstore.api.v1.release.parser import (
    AppMetaData,
    GunZipAppMetadataExtractor,
)
from nextcloudappstore.api.v1.release.provider import (
    AppReleaseProvider,
    InvalidAppDirectoryException,
)
from nextcloudappstore.core.facades import (
    read_relative_file,
    resolve_file_relative_path,
)


class FakeDownload:
    filename = resolve_file_relative_path(__file__, "data/infoxmls/minimal.xml")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ImporterTest(TestCase):
    def setUp(self):
        self.container = Container()

    def test_invalid_app_id(self):
        xml = read_relative_file(__file__, "data/infoxmls/minimal.xml")
        downloader = self.container.resolve(AppReleaseDownloader)
        downloader.get_archive = MagicMock(return_value=FakeDownload())
        extractor = self.container.resolve(GunZipAppMetadataExtractor)
        extractor.extract_app_metadata = MagicMock(return_value=AppMetaData(xml, "", "new", "change"))
        provider = self.container.resolve(AppReleaseProvider)

        with self.assertRaises(InvalidAppDirectoryException):
            provider.get_release_info("http://google.com")
