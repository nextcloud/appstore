"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import os
import tempfile
from typing import Any

import requests
from rest_framework.exceptions import ValidationError  # type: ignore

from nextcloudappstore.api.v1.release.parser import UnsupportedAppArchiveException


class MaximumDownloadSizeExceededException(ValidationError):
    pass


class DownloadException(ValidationError):
    pass


class ReleaseDownload:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def __enter__(self) -> "ReleaseDownload":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        os.remove(self.filename)


class AppReleaseDownloader:
    def get_archive(
        self,
        url: str,
        target_directory: str,
        timeout: int = 60,
        max_redirects: int = 10,
        max_size: int = 50 * (1024**2),
    ) -> ReleaseDownload:
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
        :raises DownloadException: if any HTTP or connection error occured
        :return the path to the downloaded file
        """

        if target_directory is None:
            file = tempfile.NamedTemporaryFile(delete=False)
        else:
            os.makedirs(target_directory, mode=0o700, exist_ok=True)
            file = tempfile.NamedTemporaryFile(dir=target_directory, delete=False)
        try:
            with requests.Session() as session:
                session.max_redirects = max_redirects
                req = session.get(url, stream=True, timeout=timeout)
                req.raise_for_status()
                self._stream_to_file(file, max_size, req)
        except requests.exceptions.RequestException:
            """
            We previously passed the whole error message to the client which
            is unwanted in case of a malicious client - the error message could
            be compared to a legitimate parser error message to query third
            parties' for availability/status.
            To prevent this, in case any download issue happens we raise an
            error which states that the "file" is not a valid tar.gz archive.
            This is technically correct but might not be the best UX, however
            it's definitely the best we can do now given security circumstances
            """
            filename = url[url.rfind("/") + 1 :]
            raise UnsupportedAppArchiveException(f"{filename} is not a valid tar.gz archive ")
        return ReleaseDownload(file.name)

    def _stream_to_file(self, file: Any, max_size: int, req: requests.Response) -> None:
        # start streaming download
        finished = False
        try:
            size = 0
            for chunk in req.iter_content(1024):
                file.write(chunk)
                size += len(chunk)
                if size > max_size:
                    msg = f"Downloaded archive is bigger than the allowed {max_size} bytes"
                    raise MaximumDownloadSizeExceededException(msg)
            finished = True
        finally:
            # in case any errors occurred, get rid of the file
            file.close()
            if not finished:
                os.remove(file.name)
