from django.forms import Form, CharField, Textarea, ChoiceField, RadioSelect, \
    BooleanField
from django.utils.translation import ugettext_lazy as _  # type: ignore

from nextcloudappstore.core.models import App, AppRating

RATING_CHOICES = (
    (0.0, _('Bad')),
    (0.5, _('Ok')),
    (1.0, _('Good'))
)


class AppReleaseUploadForm(Form):
    download = CharField(label=_('Download link (tar.gz)'), max_length=256)
    signature = CharField(widget=Textarea, label=_('SHA512 signature'),
                          help_text=_(
                              'Hint: can be calculated by executing the '
                              'following command: openssl dgst -sha512 -sign '
                              '/path/to/private-cert.key /path/to/app.tar.gz '
                              '| openssl base64'))
    nightly = BooleanField(label=_('Nightly'))


class AppRatingForm(Form):
    def __init__(self, *args, **kwargs):
        self._id = kwargs.pop('id', None)
        self._user = kwargs.pop('user', None)
        self._language_code = kwargs.pop('language_code', None)
        super().__init__(*args, **kwargs)

    rating = ChoiceField(initial=0.5, choices=RATING_CHOICES,
                         widget=RadioSelect)
    comment = CharField(widget=Textarea, required=False,
                        label=_('Review'))

    class Meta:
        fields = ('rating', 'comment')

    def save(self):
        app = App.objects.get(id=self._id)
        app_rating, created = AppRating.objects.get_or_create(user=self._user,
                                                              app=app)
        app_rating.rating = self.cleaned_data['rating']
        app_rating.set_current_language(self._language_code)
        app_rating.comment = self.cleaned_data['comment']
        app_rating.save()
