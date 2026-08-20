"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import re
from urllib.parse import urlparse, urlunparse

from rest_framework.exceptions import ValidationError

PEERTUBE_PATH = re.compile(
    r"^/(w|videos/watch|videos/embed)/(?P<video_id>[A-Za-z0-9_-]+)/?$",
)


class InvalidPeerTubeUrl(ValidationError):
    """Raised when a URL is not a recognized PeerTube watch or embed URL."""


def peertube_embed_url(url: str) -> str:
    """Normalize a PeerTube watch/short/embed URL to an embed URL.

    Accepts:
    - https://host/w/<id>
    - https://host/videos/watch/<id>
    - https://host/videos/embed/<id>
    """
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise InvalidPeerTubeUrl(f"PeerTube URL must be HTTPS with a host: {url}")

    match = PEERTUBE_PATH.match(parsed.path)
    if not match:
        raise InvalidPeerTubeUrl(f"PeerTube URL path must be /w/<id>, /videos/watch/<id>, or /videos/embed/<id>: {url}")

    video_id = match.group("video_id")
    return urlunparse(("https", parsed.netloc, f"/videos/embed/{video_id}", "", "", ""))
