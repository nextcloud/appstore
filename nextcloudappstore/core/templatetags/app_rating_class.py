from django import template

register = template.Library()


def raise_value_error(msg):
    raise ValueError(msg)


to_rating_class = (
    (lambda r: r <= 0.2, 'very-negative-rating'),
    (lambda r: r <= 0.4, 'negative-rating'),
    (lambda r: r <= 0.6, 'neutral-rating'),
    (lambda r: r <= 0.8, 'positive-rating'),
    (lambda r: r <= 1.0, 'very-positive-rating'),
    (lambda r: raise_value_error('Invalid rating: ' + r), None)
)


@register.filter(name='app_rating_class')
def app_rating_class(value):
    for predicate, clazz in to_rating_class:
        if predicate(value):
            return clazz
