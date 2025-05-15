"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from bleach import clean
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from markdown import markdown as default_markdown

register = template.Library()


@register.filter(name="markdown")
def markdown(sentence):
    text = default_markdown(sentence)
    safe_text = clean(text, attributes=settings.MARKDOWN_ALLOWED_ATTRIBUTES, tags=settings.MARKDOWN_ALLOWED_TAGS)
    return mark_safe(safe_text)  # nosec
