from django import template

register = template.Library()


@register.filter(name='css_class')
def css_class(value, arg):
    return value.as_widget(attrs={'class': arg})
