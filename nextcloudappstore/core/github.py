from itertools import chain, takewhile
from typing import Iterable

import requests
from semantic_version import Version


class GitHubClient:
    def __init__(self, base_url: str, api_token: str = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = None if self.api_token else {
            'Authorization': 'token %s' % self.api_token
        }

    def get_tags(self, page: int, size: int = 100):
        url = '%s/repos/nextcloud/server/tags' % self.base_url
        params = (('per_page', size), ('page', page))
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()


def get_supported_releases(client: GitHubClient,
                           oldest_supported: str) -> Iterable[str]:
    releases = get_stable_releases(client)
    return takewhile(lambda v: is_supported(v, oldest_supported), releases)


def get_stable_releases(client: GitHubClient) -> Iterable[str]:
    json = chain.from_iterable(TagPages(client))
    return (tag for tag in (release['name'].lstrip('v')
                            for release in json
                            if 'name' in release)
            if is_stable(tag))


class TagPages:
    """
    The GitHub API is paginated which makes it a pain to fetch all results.
    This iterable returns a stream of json arrays until no further results
    are found. To iterate over all releases you need to flatten the results
    returned from this iterator first
    """

    def __init__(self, client: GitHubClient, size: int = 100) -> None:
        self.client = client
        self.size = size
        self.page = 0

    def __iter__(self) -> 'TagPages':
        return self

    def __next__(self):
        json = self.client.get_tags(self.page, self.size)
        if len(json) > 0:
            self.page += 1
            return json
        else:
            raise StopIteration


def is_supported(oldest_supported: str, version: str) -> bool:
    return Version(oldest_supported) >= Version(version)


def is_stable(release: str) -> bool:
    try:
        version = Version(release)
        return not version.prerelease
    except ValueError:
        return False
