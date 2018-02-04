import json
from typing import Dict, Any
from unittest.mock import MagicMock

from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.github import GitHubClient, get_supported_releases


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

    def _get_tags(self, page: int, size: int = 100) -> Dict[Any, Any]:
        return json.loads(self._read('tags_page_%d.json' % page))

    def _read(self, path: str) -> str:
        return read_relative_file(__file__, 'data/%s' % path)
