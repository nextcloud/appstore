from django.conf import settings
from django.utils.safestring import mark_safe
from django import template
from markdown import markdown as default_markdown
from bleach import clean

register = template.Library()


@register.filter(name='markdown')
def markdown(sentence):
    text = default_markdown(sentence)
    safe_text = clean(text,
                      attributes=settings.MARKDOWN_ALLOWED_ATTRIBUTES,
                      tags=settings.MARKDOWN_ALLOWED_TAGS)
    return mark_safe(safe_text)  # nosec
