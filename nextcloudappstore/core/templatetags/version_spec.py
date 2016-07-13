from django import template

register = template.Library()


@register.filter()
def version_spec(value):
    if value == '*':
        return ''
    else:
        return value
