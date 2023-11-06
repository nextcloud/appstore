from django import template
from django.utils.translation import gettext_lazy as _  # type: ignore

register = template.Library()

to_rating = (
    (lambda r: r <= 0.2, _("Very negative")),
    (lambda r: r <= 0.4, _("Negative")),
    (lambda r: r <= 0.6, _("Neutral")),
    (lambda r: r <= 0.8, _("Positive")),
    (lambda r: True, _("Very positive")),
)

to_rating_img = (
    (lambda r: r <= 0.2, 1),
    (lambda r: r <= 0.4, 3),
    (lambda r: r <= 0.6, 6),
    (lambda r: r <= 0.8, 8),
    (lambda r: True, 10),
)


@register.filter(name="app_rating")
def app_rating(value):
    for predicate, rating in to_rating:
        if predicate(value):
            return rating


@register.filter(name="app_rating_img")
def app_rating_img(value):
    for predicate, rating in to_rating_img:
        if predicate(value):
            return rating
