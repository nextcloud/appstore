from django.forms import Form, CharField, Textarea, ChoiceField, RadioSelect
from django.utils.translation import ugettext_lazy as _  # type: ignore

RATING_CHOICES = (
    (0.0, _('Bad')),
    (0.5, _('Ok')),
    (1.0, _('Good'))
)


class AppRatingForm(Form):
    rating = ChoiceField(initial=0.5, choices=RATING_CHOICES,
                         widget=RadioSelect)
    comment = CharField(widget=Textarea, required=False,
                        label=_('Rating comment'))

    class Meta:
        fields = ('rating', 'comment')
