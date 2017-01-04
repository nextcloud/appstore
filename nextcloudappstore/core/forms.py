from django.conf import settings
from django.forms import Form, CharField, Textarea, ChoiceField, RadioSelect, \
    BooleanField, TextInput
from django.utils.translation import get_language_info, ugettext_lazy as _  # type: ignore

from nextcloudappstore.core.models import App, AppRating

RATING_CHOICES = (
    (0.0, _('Bad')),
    (0.5, _('Ok')),
    (1.0, _('Good'))
)


class AppReleaseUploadForm(Form):
    download = CharField(label=_('Download link (tar.gz)'), max_length=256,
                         widget=TextInput(attrs={'required': 'required'}))
    signature = CharField(widget=Textarea(attrs={'required': 'required'}),
                          label=_('SHA512 signature'),
                          help_text=_(
                              'Can be generated by executing the '
                              'following command: <b>openssl dgst -sha512 '
                              '-sign ~/.nextcloud/certificates/APP_ID.key '
                              '/path/to/app.tar.gz | openssl base64</b>'))
    nightly = BooleanField(label=_('Nightly'), required=False)
    safe_help_fields = ['signature']


class AppRegisterForm(Form):
    certificate = CharField(
        widget=Textarea(attrs={'required': 'required'}),
        label=_('Public certificate'),
        help_text=_(
            'Usually stored in ~/.nextcloud/certificates/APP_ID.crt where '
            'APP_ID is your app\'s id. If you do not have a certificate you '
            'need to create a certificate sign request (CSR) first which '
            'should be posted on the <a '
            'href="https://github.com/nextcloud/app-certificate-requests" '
            'rel="noreferrer noopener">certificate repository</a> (follow '
            'the README). You can generate the CSR by executing the '
            'following command: <b>openssl req -nodes -newkey rsa:4096 '
            '-keyout APP_ID.key -out APP_ID.csr -subj "/CN=APP_ID"</b>'))
    signature = CharField(widget=Textarea(attrs={'required': 'required'}),
                          label=_('SHA512 signature over your app\'s id'),
                          help_text=_(
                              'Can be generated by executing the '
                              'following '
                              'command: <b>echo -n "APP_ID" | openssl dgst '
                              '-sha512 -sign '
                              '~/.nextcloud/certificates/APP_ID.key | '
                              'openssl base64</b>'))
    safe_help_fields = ['certificate', 'signature']

def get_languages_local(language=None):
    if language:
        languages = list(language)
    else:
        languages = [ l[0] for l in settings.LANGUAGES]

    language_infos = list()
    for l in languages:
        lang_info =  get_language_info(l)
        language_infos.append((lang_info['code'], lang_info['name_local']))

    return language_infos

class AppRatingForm(Form):
    def __init__(self, *args, **kwargs):
        self._id = kwargs.pop('id', None)
        self._user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    rating = ChoiceField(initial=0.5, choices=RATING_CHOICES,
                         widget=RadioSelect)
    comment = CharField(widget=Textarea, required=False,
                        label=_('Comment'))

    language_code = ChoiceField(initial="", choices=get_languages_local())

    class Meta:
        fields = ('rating', 'comment', 'language_code')

    def save(self):
        app = App.objects.get(id=self._id)
        app_rating, created = AppRating.objects.get_or_create(user=self._user,
                                                              app=app)
        app_rating.rating = self.cleaned_data['rating']
        app_rating.set_current_language(self.cleaned_data['language_code'])
        app_rating.comment = self.cleaned_data['comment']
        app_rating.save()
