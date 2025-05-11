"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later

Queries the live API and import all releases locally for a Nextcloud version
"""

import sys

from requests import get

from . import ADMIN, import_app, import_release

APPS_URL = "https://apps.nextcloud.com/api/v1/platform/%s/apps.json"


def main():
    version = sys.argv[1]
    apps = get(APPS_URL % version).json()
    for app in apps:
        import_app(app["certificate"], "signature", ADMIN)
        for release in app["releases"]:
            import_release(release["download"], release["signature"], release["isNightly"], ADMIN)


if __name__ == "__main__":
    main()
