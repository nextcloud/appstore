from django.conf import settings  # type: ignore

from nextcloudappstore.core.facades import read_relative_file


class ReleaseConfig:
    def __init__(self) -> None:
        self.download_root = settings.RELEASE_DOWNLOAD_ROOT  # type: str
        self.max_file_size = settings.MAX_DOWNLOAD_FILE_SIZE
        self.download_max_timeout = settings.MAX_DOWNLOAD_TIMEOUT
        self.download_max_redirects = settings.MAX_DOWNLOAD_REDIRECTS
        self.download_max_size = settings.MAX_DOWNLOAD_SIZE
        self.info_schema = read_relative_file(__file__, 'info.xsd')
        self.info_xslt = read_relative_file(__file__, 'info.xslt')
        self.pre_info_xslt = read_relative_file(__file__, 'pre-info.xslt')
        self.db_schema = read_relative_file(__file__, 'database.xsd')
        self.pre_db_xslt = read_relative_file(__file__, 'pre-database.xslt')
        self.languages = settings.LANGUAGES
        self.member_blacklist = settings.ARCHIVE_FOLDER_BLACKLIST
