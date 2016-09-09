from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor, parse_app_metadata
from hashlib import sha512
from typing import Dict

from rest_framework.exceptions import APIException


class InvalidAppDirectoryException(APIException):
    pass


class AppReleaseProvider:
    def __init__(self, downloader: AppReleaseDownloader,
                 extractor: GunZipAppMetadataExtractor,
                 config: ReleaseConfig) -> None:
        self.config = config
        self.extractor = extractor
        self.downloader = downloader

    def get_release_info(self, url: str) -> Dict:
        with self.downloader.get_archive(
            url, self.config.download_root, self.config.download_max_timeout,
            self.config.download_max_redirects, self.config.download_max_size
        ) as download:
            xml, archive_app_folder = self.extractor.extract_app_metadata(
                download.filename)
            info = parse_app_metadata(xml, self.config.info_schema,
                                      self.config.pre_info_xslt,
                                      self.config.info_xslt)
            info_app_id = info['app']['id']
            if archive_app_folder != info_app_id:
                msg = 'Archive app folder is %s but info.xml reports id %s' \
                      % (archive_app_folder, info_app_id)
                raise InvalidAppDirectoryException(msg)

            # generate sha256sum for archive
            with open(download.filename, 'rb') as f:
                checksum = sha512(f.read()).hexdigest()
        return info, checksum
