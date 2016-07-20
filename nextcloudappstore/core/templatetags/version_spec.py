from django import template
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter()
def version_spec(value):
    if value == '*':
        return _('all versions')
    else:
        return value
