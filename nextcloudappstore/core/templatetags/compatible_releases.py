"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django import template

from nextcloudappstore.core.models import App, AppRelease

register = template.Library()


@register.filter(name="compatible_releases")
def compatible_releases(app: App, version: str) -> AppRelease:
    return app.compatible_releases(version)
