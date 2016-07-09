from django import template
from nextcloudappstore.core.versioning import pad_min_version
from semantic_version import Version

register = template.Library()


@register.filter()
def sort_by_version(value, arg):
    reverse = True if arg == 'desc' else False
    ret_list = []
    for key in sorted(value.keys(), reverse=reverse,
                      key=lambda v: Version(pad_min_version(v))):
        ret_list.append((key, value[key]))
    return ret_list
