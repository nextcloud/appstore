from django.conf import settings  # type: ignore
from nextcloudappstore.core.facades import read_relative_file


class ReleaseConfig:
    def __init__(self) -> None:
        self.max_info_size = 512 * 1024  # bytes
        self.download_root = settings.RELEASE_DOWNLOAD_ROOT  # type: str
        self.download_max_timeout = 60
        self.download_max_redirects = 10
        self.download_max_size = 20 * (1024 ** 2)
        self.info_schema = read_relative_file(__file__, 'info.xsd')
        self.info_xslt = read_relative_file(__file__, 'info.xslt')
