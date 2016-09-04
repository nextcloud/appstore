from django import template

register = template.Library()


@register.filter(name='field_type')
def field_type(field):
    return field.field.__class__.__name__
