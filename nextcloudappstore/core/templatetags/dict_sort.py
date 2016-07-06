from django import template

register = template.Library()


@register.filter()
def dict_sort(value, arg):
    reverse = True if arg == 'desc' else False
    ret_list = []
    for key in sorted(value.keys(), reverse=reverse):
        ret_list.append((key, value[key]))
    return ret_list
