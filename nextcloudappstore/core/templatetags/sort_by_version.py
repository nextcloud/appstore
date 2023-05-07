from django import template
from nextcloudappstore.core.versioning import pad_min_version
from semantic_version import Version

register = template.Library()


@register.filter()
def sort_by_version(value, arg):
    reverse = arg == 'desc'
    return [(key, value[key]) for key in sorted(value.keys(), reverse=reverse,
            key=lambda v: Version(pad_min_version(v)))]
