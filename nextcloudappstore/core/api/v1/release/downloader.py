import tempfile

import requests
import uuid
import os

from typing import Any

from rest_framework.exceptions import APIException  # type: ignore


class MaximumDownloadSizeExceededException(APIException):
    pass


class ReleaseDownload:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def __enter__(self) -> 'ReleaseDownload':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        os.remove(self.filename)


class AppReleaseDownloader:
    def get_archive(self, url: str, target_directory: str, timeout: int = 60,
                    max_redirects: int = 10,
                    max_size: int = 50 * (1024 ** 2)) -> ReleaseDownload:
        """
        Downloads an app release from an url to a directory
        :argument target_directory directory where the downloaded archive
        should be saved, will be created if it does not exist yet
        :argument url to the archive
        :argument timeout maximum timeout in seconds
        :argument max_redirects number of maximum redirects to follow,
        defaults to 10
        :argument max_size how big the archive is allowed to be in bytes,
        defaults to 50Mb
        :raises MaximumDownloadSizeExceededException if the archive is bigger
        than allowed
        :raises requests.HttpError for non 2xx status codes
        :raises requests.ConnectionError for failed connections
        :raises requests.TooManyRedirects of too many redirects were made
        :return the path to the downloaded file
        """

        if target_directory is None:
            file = tempfile.NamedTemporaryFile(delete=False)
        else:
            os.makedirs(target_directory, mode=0o755, exist_ok=True)
            file = tempfile.NamedTemporaryFile(dir=target_directory,
                                               delete=False)

        with requests.Session() as session:
            session.max_redirects = max_redirects
            req = session.get(url, stream=True, timeout=timeout)
            req.raise_for_status()
            if int(req.headers.get('Content-Length')) > max_size:
                msg = 'Downloaded archive is bigger than the allowed %i ' \
                      'bytes' % max_size
                raise MaximumDownloadSizeExceededException(msg)

            self._stream_to_file(file, max_size, req)

        return ReleaseDownload(file.name)

    def _stream_to_file(self, file: Any, max_size: int,
                        req: requests.Response) -> None:
        # start streaming download
        finished = False
        try:
            size = 0
            for chunk in req.iter_content(1024):
                file.write(chunk)
                size += len(chunk)
                if size > max_size:
                    msg = 'Downloaded archive is bigger than the ' \
                          'allowed %i bytes' % max_size
                    raise MaximumDownloadSizeExceededException(msg)
            finished = True
        finally:
            # in case any errors occurred, get rid of the file
            if not finished:
                os.remove(file.name)
