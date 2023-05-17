import json
from io import StringIO
from typing import Any, Dict
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.github import GitHubClient
from nextcloudappstore.core.models import NextcloudRelease


class SyncNextcloudReleasesTest(TestCase):
    @patch.object(GitHubClient, "get_tags")
    def test_sync(self, get_tags):
        get_tags.side_effect = self._get_tags
        call_command("syncnextcloudreleases", "--oldest-supported=11.0.0", stdout=StringIO())

        latest = NextcloudRelease.objects.get(version="12.0.5")
        self.assertEquals(True, latest.is_current)
        self.assertEquals(True, latest.has_release)
        self.assertEquals(True, latest.is_supported)

    @patch.object(GitHubClient, "get_tags")
    def test_sync_print(self, get_tags):
        get_tags.side_effect = self._get_tags
        io = StringIO()
        call_command("syncnextcloudreleases", "--oldest-supported=11.0.0", "--print", stdout=io)
        expected = (
            "\n".join(
                [
                    "12.0.5",
                    "12.0.4",
                    "12.0.3",
                    "12.0.2",
                    "12.0.1",
                    "12.0.0",
                    "11.0.7",
                    "11.0.6",
                    "11.0.5",
                    "11.0.4",
                    "11.0.3",
                    "11.0.2",
                    "11.0.1",
                    "11.0.0",
                ]
            )
            + "\n"
        )
        self.assertEquals(0, NextcloudRelease.objects.count())

        io.seek(0)
        self.assertEquals(expected, io.read())

    def _get_tags(self, page: int, size: int = 100) -> Dict[Any, Any]:
        return json.loads(self._read("tags_page_%d.json" % page))

    def _read(self, path: str) -> str:
        return read_relative_file(__file__, "../../../tests/data/%s" % path)
