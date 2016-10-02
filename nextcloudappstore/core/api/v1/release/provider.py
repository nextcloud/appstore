from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor, parse_app_metadata, parse_changelog
from typing import Dict, Tuple

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

    def get_release_info(self, url: str, is_nightly: bool = False) -> Tuple[
                                                                    Dict, str]:
        data = None
        with self.downloader.get_archive(
            url, self.config.download_root, self.config.download_max_timeout,
            self.config.download_max_redirects, self.config.download_max_size
        ) as download:
            xml, app_id, changelog = self.extractor.extract_app_metadata(
                download.filename)
            info = parse_app_metadata(xml, self.config.info_schema,
                                      self.config.pre_info_xslt,
                                      self.config.info_xslt)
            info_app_id = info['app']['id']
            if app_id != info_app_id:
                msg = 'Archive app folder is %s but info.xml reports id %s' \
                      % (app_id, info_app_id)
                raise InvalidAppDirectoryException(msg)

            version = info['app']['release']['version']
            if is_nightly:
                version += '-nightly'
            info['app']['release']['changelog'] = parse_changelog(changelog,
                                                                  version)

            with open(download.filename, 'rb') as f:
                data = f.read()
        return info, data
