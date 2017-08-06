from django import template
from django.utils.translation import ugettext_lazy as _  # type: ignore

register = template.Library()

to_rating = (
    (lambda r: r <= 0.2, _('Very negative')),
    (lambda r: r <= 0.4, _('Negative')),
    (lambda r: r <= 0.6, _('Neutral')),
    (lambda r: r <= 0.8, _('Positive')),
    (lambda r: True, _('Very positive'))
)


@register.filter(name='app_rating')
def app_rating(value):
    for predicate, rating in to_rating:
        if predicate(value):
            return rating
