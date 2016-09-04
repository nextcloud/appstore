from django import template
from django.utils.translation import ugettext_lazy as _  # type: ignore

register = template.Library()


def raise_value_error(msg):
    raise ValueError(msg)


to_rating = (
    (lambda r: r <= 0.2, _('Very negative')),
    (lambda r: r <= 0.4, _('Negative')),
    (lambda r: r <= 0.6, _('Neutral')),
    (lambda r: r <= 0.8, _('Positive')),
    (lambda r: r <= 1.0, _('Very positive')),
    (lambda r: raise_value_error('Invalid rating: ' + r), None)
)


@register.filter(name='app_rating')
def app_rating(value):
    for predicate, rating in to_rating:
        if predicate(value):
            return rating
