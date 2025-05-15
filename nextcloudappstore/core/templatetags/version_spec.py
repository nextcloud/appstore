"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django import template

register = template.Library()


@register.filter()
def version_spec(value):
    if value == "*":
        return ""
    else:
        return value
