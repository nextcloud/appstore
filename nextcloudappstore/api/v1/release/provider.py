from typing import Any, Dict, Tuple

from rest_framework.exceptions import ValidationError

from nextcloudappstore.api.v1.release import ReleaseConfig
from nextcloudappstore.api.v1.release.downloader import AppReleaseDownloader
from nextcloudappstore.api.v1.release.parser import (
    GunZipAppMetadataExtractor,
    parse_app_metadata,
    parse_changelog,
    validate_database,
)


class InvalidAppDirectoryException(ValidationError):
    pass


Release = Tuple[Dict[Any, Any], bytes]


class AppReleaseProvider:
    def __init__(
        self, downloader: AppReleaseDownloader, extractor: GunZipAppMetadataExtractor, config: ReleaseConfig
    ) -> None:
        self.config = config
        self.extractor = extractor
        self.downloader = downloader

    def get_release_info(self, url: str, is_nightly: bool = False) -> Release:
        data = None
        with self.downloader.get_archive(
            url,
            self.config.download_root,
            self.config.download_max_timeout,
            self.config.download_max_redirects,
            self.config.download_max_size,
        ) as download:
            meta = self.extractor.extract_app_metadata(download.filename)
            info = parse_app_metadata(
                meta.info_xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt
            )
            if meta.database_xml:
                validate_database(meta.database_xml, self.config.db_schema, self.config.pre_db_xslt)
            info_app_id = info["app"]["id"]
            if meta.app_id != info_app_id:
                msg = "Archive app folder is %s but info.xml reports id %s" % (meta.app_id, info_app_id)
                raise InvalidAppDirectoryException(msg)

            release = info["app"]["release"]
            info["app"]["release"]["is_nightly"] = is_nightly
            version = release["version"]
            release["changelog"] = meta.changelog
            for code, value in meta.changelog.items():
                release["changelog"][code] = parse_changelog(value, version, is_nightly)

            with open(download.filename, "rb") as f:
                data = f.read()
        return info, data
