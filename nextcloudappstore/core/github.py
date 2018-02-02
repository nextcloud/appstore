from itertools import chain, takewhile
from typing import Iterable

import requests
from semantic_version import Version


def get_supported_releases(oldest_supported: str, url: str, api_token: str = None) -> Iterable[str]:
    releases = get_stable_releases(url, api_token)
    return takewhile(lambda v: is_supported(v, oldest_supported), releases)


def get_stable_releases(url: str, api_token: str = None) -> Iterable[str]:
    json = chain.from_iterable([tags for tags in TagPages(api_token, url)])
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

    def __init__(self, api_token: str, url: str, size: int = 100):
        self.url = url
        self.api_token = api_token
        self.size = size
        self.headers = None if self.api_token is None else {
            'Authorization': 'token %s' % self.api_token
        }
        self.page = 0

    def __iter__(self) -> 'TagPages':
        return self

    def __next__(self):
        params = (('per_page', self.size), ('page', self.page))
        response = requests.get(self.url, params=params, headers=self.headers)
        response.raise_for_status()
        json = response.json()

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
