"""
SPDX-FileCopyrightText: 2018 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import base64
import re
import time
from collections.abc import Iterable
from itertools import chain, takewhile
from typing import Any
from urllib.parse import quote

import requests
from semantic_version import Version

from nextcloudappstore.core.models import NextcloudRelease

_GITHUB_RELEASE_URL_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)/releases/download/([^/]+)/(.+)$")


def parse_github_release_url(url: str) -> tuple[str, str, str, str] | None:
    """Parse a GitHub release asset URL into (owner, repo, tag, filename), or None."""
    m = _GITHUB_RELEASE_URL_RE.match(url)
    return (m.group(1), m.group(2), m.group(3), m.group(4)) if m else None


class GitHubClient:
    def __init__(self, base_url: str, api_token: str = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {"Authorization": f"token {self.api_token}"} if self.api_token else None

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, headers=self.headers, timeout=21, **kwargs)
        response.raise_for_status()
        return response

    def get_tags(self, page: int, size: int = 100):
        return self._request(
            "GET",
            "/repos/nextcloud/server/tags",
            params=(("per_page", size), ("page", page)),
        ).json()

    def get_releases(self, owner: str, repo: str) -> list:
        releases = []
        page = 1
        while True:
            page_data = self._request(
                "GET",
                f"/repos/{owner}/{repo}/releases",
                params={"per_page": 100, "page": page},
            ).json()
            if not page_data:
                break
            releases.extend(page_data)
            page += 1
        return releases

    def get_repository(self, owner: str, repo: str) -> dict:
        return self._request("GET", f"/repos/{owner}/{repo}").json()

    def get_ref_sha(self, owner: str, repo: str, ref: str) -> str:
        """Return the commit SHA for a git ref such as ``heads/master``."""
        data = self._request("GET", f"/repos/{owner}/{repo}/git/ref/{ref}").json()
        return data["object"]["sha"]

    def create_branch(self, owner: str, repo: str, branch: str, sha: str) -> None:
        self._request(
            "POST",
            f"/repos/{owner}/{repo}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": sha},
        )

    def delete_branch(self, owner: str, repo: str, branch: str) -> None:
        self._request("DELETE", f"/repos/{owner}/{repo}/git/refs/heads/{quote(branch)}")

    def get_content_sha(self, owner: str, repo: str, path: str, ref: str) -> str | None:
        """Return the blob SHA for a path on ``ref``, or None if missing."""
        encoded_path = quote(path)
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{encoded_path}"
        response = requests.get(url, params={"ref": ref}, headers=self.headers, timeout=21)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["sha"]

    def create_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
    ) -> None:
        encoded_path = quote(path)
        self._request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/{encoded_path}",
            json={
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            },
        )

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict:
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
        ).json()


class AppCertificateExistsError(Exception):
    """Raised when the certificate-requests repo already has this app id."""


def create_app_certificate_request_pr(
    client: GitHubClient,
    certificate_repo: str,
    app_id: str,
    csr: str,
    repository_url: str,
    submitter: str,
) -> str:
    """
    Open a PR on the certificate-requests repo adding ``APP_ID/APP_ID.csr``.

    Raises ``AppCertificateExistsError`` if ``APP_ID.csr`` or
    ``APP_ID.crt`` already exists on the default branch.

    Returns the pull request HTML URL.
    """
    owner, repo = certificate_repo.split("/", 1)
    repository = client.get_repository(owner, repo)
    base_branch = repository["default_branch"]
    base_ref = f"refs/heads/{base_branch}"
    csr_path = f"{app_id}/{app_id}.csr"
    crt_path = f"{app_id}/{app_id}.crt"
    if client.get_content_sha(owner, repo, csr_path, base_ref) or client.get_content_sha(
        owner, repo, crt_path, base_ref
    ):
        raise AppCertificateExistsError(app_id)

    base_sha = client.get_ref_sha(owner, repo, f"heads/{base_branch}")

    # Avoid slashes in branch names; they complicate refs and the Contents API.
    branch = f"appstore-{app_id}-{int(time.time())}"
    client.create_branch(owner, repo, branch, base_sha)

    try:
        client.create_file(
            owner,
            repo,
            csr_path,
            csr if csr.endswith("\n") else csr + "\n",
            f"Add certificate request for {app_id}",
            branch,
        )

        body = (
            "### Checklist\n\n"
            f"- Please include a link to your app repository: {repository_url}\n\n"
            f"Submitted via the Nextcloud App Store by {submitter}."
        )
        pull = client.create_pull_request(
            owner,
            repo,
            title=f"Add certificate request for {app_id}",
            body=body,
            head=branch,
            base=base_branch,
        )
    except Exception:
        try:
            client.delete_branch(owner, repo, branch)
        except requests.RequestException:
            pass
        raise

    return pull["html_url"]


def sync_releases(versions: Iterable[str]) -> None:
    """
    All given versions have a release. If a release is absent, persisted
    releases are out of date and need to have their release flag removed.
    Finally the latest version must be marked as current.
    :param versions: an iterable yielding all retrieved GitHub tags
    :return:
    """
    current_releases = NextcloudRelease.objects.all()
    imported_releases = [NextcloudRelease.objects.get_or_create(version=version)[0] for version in versions]
    if imported_releases:
        # all imported releases have a release, existing ones don't
        for release in imported_releases:
            release.is_supported = True
            release.has_release = True
            release.save()
        for release in get_old_releases(current_releases, imported_releases):
            release.is_supported = False
            release.save()
        # set latest release
        NextcloudRelease.objects.update(is_current=False)
        latest = max(imported_releases, key=lambda v: Version(v.version))
        latest.is_current = True
        latest.save()


NextcloudReleases = list[NextcloudRelease]


def get_old_releases(current: NextcloudReleases, imported: NextcloudReleases) -> NextcloudReleases:
    imported_versions = {release.version for release in imported}
    return [release for release in current if release.version not in imported_versions]


def get_supported_releases(client: GitHubClient, oldest_supported: str) -> Iterable[str]:
    releases = get_stable_releases(client)
    return takewhile(lambda v: is_supported(v, oldest_supported), releases)


def get_stable_releases(client: GitHubClient) -> Iterable[str]:
    json = chain.from_iterable(TagPages(client))
    return (tag for tag in (release["name"].lstrip("v") for release in json if "name" in release) if is_stable(tag))


def is_supported(oldest_supported: str, version: str) -> bool:
    return Version(oldest_supported) >= Version(version)


def is_stable(release: str) -> bool:
    try:
        version = Version(release)
        return not version.prerelease
    except ValueError:
        return False


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
        self.page = 1  # pages are 1 indexed

    def __iter__(self) -> "TagPages":
        return self

    def __next__(self):
        json = self.client.get_tags(self.page, self.size)
        if len(json) > 0:
            self.page += 1
            return json
        else:
            raise StopIteration


def get_download_counts(releases: list, client: GitHubClient) -> list[dict]:
    """
    Return per-release download counts fetched from the GitHub releases API.

    Each entry in the returned list corresponds to one AppRelease and contains:
      version, is_nightly, download (the URL), download_count (int or None).

    Counts are None for releases not hosted on GitHub or when the GitHub API
    call fails (e.g. rate-limited, private repo, network error).
    """
    # Group releases by (owner, repo) to minimise API calls.
    repo_to_releases: dict[tuple[str, str], list[tuple[str, str, object]]] = {}
    for release in releases:
        parsed = parse_github_release_url(release.download)
        if parsed:
            owner, repo, tag, filename = parsed
            repo_to_releases.setdefault((owner, repo), []).append((tag, filename, release))

    # Build (owner, repo, tag, filename) -> download_count lookup.
    count_map: dict[tuple[str, str, str, str], int] = {}
    for owner, repo in repo_to_releases:
        try:
            gh_releases = client.get_releases(owner, repo)
            for gh_release in gh_releases:
                tag_name = gh_release.get("tag_name", "")
                for asset in gh_release.get("assets", []):
                    count_map[(owner, repo, tag_name, asset["name"])] = asset["download_count"]
        except requests.RequestException:
            pass

    result = []
    for release in releases:
        parsed = parse_github_release_url(release.download)
        if parsed:
            owner, repo, tag, filename = parsed
            count = count_map.get((owner, repo, tag, filename))
        else:
            count = None
        result.append(
            {
                "version": release.version,
                "is_nightly": release.is_nightly,
                "download": release.download,
                "download_count": count,
            }
        )
    return result
