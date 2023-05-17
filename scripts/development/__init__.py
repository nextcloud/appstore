import sys
from typing import Tuple

from requests import post

REGISTER_URL = "http://127.0.0.1:8000/api/v1/apps"
RELEASE_URL = "http://127.0.0.1:8000/api/v1/apps/releases"
ADMIN = ("admin", "admin")


def handle_response(response) -> None:
    if response.status_code > 299:
        msg = "Request to url %s failed with status code %d"
        print(msg % (response.url, response.status_code), file=sys.stderr)
        print(response.text, file=sys.stderr)


def import_app(certificate: str, signature: str, auth=Tuple[str, str]) -> None:
    response = post(REGISTER_URL, auth=auth, json={"signature": signature, "certificate": certificate})
    handle_response(response)


def import_release(url: str, signature: str, nightly: bool, auth=Tuple[str, str]) -> None:
    print("Downloading app from %s" % url)
    response = post(RELEASE_URL, auth=auth, json={"download": url, "signature": signature, "nightly": nightly})
    handle_response(response)
