from django import template

register = template.Library()


@register.filter(name='ocs_categoryid')
def ocs_categoryid(id: str) -> str:
    return ''.join(map(lambda char: str(ord(char)), id[:4]))
