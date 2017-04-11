from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value: str, arg: str) -> str:
    source, target = arg.split(',')
    return value.replace(source, target)
