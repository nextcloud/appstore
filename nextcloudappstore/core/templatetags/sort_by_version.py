"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django import template
from semantic_version import Version

from nextcloudappstore.core.versioning import pad_min_version

register = template.Library()


@register.filter()
def sort_by_version(value, arg):
    reverse = arg == "desc"
    return [
        (key, value[key]) for key in sorted(value.keys(), reverse=reverse, key=lambda v: Version(pad_min_version(v)))
    ]
