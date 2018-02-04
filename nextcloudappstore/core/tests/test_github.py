import json
from typing import Dict, Any
from unittest.mock import MagicMock

from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.github import GitHubClient, \
    get_supported_releases, sync_releases
from nextcloudappstore.core.models import NextcloudRelease


class RatingTest(TestCase):

    def test_parse_tags(self):
        client = MagicMock(spec=GitHubClient)
        client.get_tags.side_effect = self._get_tags
        releases = get_supported_releases(client, '11.0.0')
        expected = [
            '11.0.0',
            '11.0.1',
            '11.0.2',
            '11.0.3',
            '11.0.4',
            '11.0.5',
            '11.0.6',
            '11.0.7',
            '12.0.0',
            '12.0.1',
            '12.0.2',
            '12.0.3',
            '12.0.4',
            '12.0.5',
        ]
        self.assertEquals(expected, sorted(list(releases)))

    def test_import_releases(self):
        client = MagicMock(spec=GitHubClient)
        client.get_tags.side_effect = self._get_tags
        releases = get_supported_releases(client, '11.0.0')

        self._create_release('10.0.0', False, True)
        self._create_release('10.0.1', True, True)
        self._create_release('11.0.0', False, False)
        self._create_release('11.0.1', True, False)

        sync_releases(releases)

        self.assertEquals(16, NextcloudRelease.objects.count())
        self.assertEquals(False, self.get_rel('10.0.0').has_release)
        self.assertEquals(False, self.get_rel('10.0.0').is_current)
        self.assertEquals(False, self.get_rel('10.0.1').has_release)
        self.assertEquals(False, self.get_rel('10.0.1').is_current)
        self.assertEquals(True, self.get_rel('11.0.0').has_release)
        self.assertEquals(False, self.get_rel('11.0.0').is_current)
        self.assertEquals(True, self.get_rel('11.0.1').has_release)
        self.assertEquals(False, self.get_rel('11.0.1').is_current)
        self.assertEquals(True, self.get_rel('12.0.4').has_release)
        self.assertEquals(False, self.get_rel('12.0.4').is_current)
        self.assertEquals(True, self.get_rel('12.0.5').has_release)
        self.assertEquals(True, self.get_rel('12.0.5').is_current)

    def get_rel(self, version: str) -> NextcloudRelease:
        return NextcloudRelease.objects.get(version=version)

    def _create_release(self, version: str, is_current: bool,
                        has_release: bool) -> NextcloudRelease:
        return NextcloudRelease.objects.create(version=version,
                                               is_current=is_current,
                                               has_release=has_release)

    def _get_tags(self, page: int, size: int = 100) -> Dict[Any, Any]:
        return json.loads(self._read('tags_page_%d.json' % page))

    def _read(self, path: str) -> str:
        return read_relative_file(__file__, 'data/%s' % path)
