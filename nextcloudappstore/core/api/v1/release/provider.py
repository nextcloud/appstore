from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor, parse_app_metadata, parse_changelog
from typing import Dict, Tuple

from rest_framework.exceptions import ValidationError


class InvalidAppDirectoryException(ValidationError):
    pass


Release = Tuple[Dict, str]


class AppReleaseProvider:
    def __init__(self, downloader: AppReleaseDownloader,
                 extractor: GunZipAppMetadataExtractor,
                 config: ReleaseConfig) -> None:
        self.config = config
        self.extractor = extractor
        self.downloader = downloader

    def get_release_info(self, url: str, is_nightly: bool = False) -> Release:
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

            release = info['app']['release']
            info['app']['release']['is_nightly'] = is_nightly
            version = release['version']
            release['changelog'] = changelog
            for code, value in changelog.items():
                release['changelog'][code] = parse_changelog(value, version,
                                                             is_nightly)

            with open(download.filename, 'rb') as f:
                data = f.read()
        return info, data
