from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor, parse_app_metadata
from hashlib import sha256
from typing import Dict


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
            xml = self.extractor.extract_app_metadata(download.filename)
            info = parse_app_metadata(xml, self.config.info_schema,
                                      self.config.info_xslt)
            # generate sha256sum for archive
            with open(download.filename, 'rb') as f:
                checksum = sha256(f.read()).hexdigest()
                info['app']['release']['checksum'] = checksum
        return info
