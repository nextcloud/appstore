from django import template

register = template.Library()


to_rating_class = (
    (lambda r: r <= 0.2, 'very-negative-rating'),
    (lambda r: r <= 0.4, 'negative-rating'),
    (lambda r: r <= 0.6, 'neutral-rating'),
    (lambda r: r <= 0.8, 'positive-rating'),
    (lambda r: True, 'very-positive-rating')
)


@register.filter(name='app_rating_class')
def app_rating_class(value):
    for predicate, clazz in to_rating_class:
        if predicate(value):
            return clazz
