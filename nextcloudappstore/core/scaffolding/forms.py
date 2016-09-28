import re
from os import listdir

from django.core.exceptions import ValidationError
from django.forms import Textarea, Form, URLField
from django.utils.translation import ugettext_lazy as _  # type: ignore
from django.forms.fields import EmailField, CharField, ChoiceField
from django.conf import settings

from nextcloudappstore.core.facades import resolve_file_relative_path

tpls = listdir(resolve_file_relative_path(__file__, 'app-templates'))
available_versions = [v for v in settings.PLATFORM_VERSIONS if v in tpls]
versions = zip(available_versions, available_versions)


def validate_id(input: str) -> str:
    regex = r'^([A-Z][a-z]+)+$'
    if not re.match(regex, input):
        raise ValidationError(_('The app name must be camel case e.g. MyApp'))


class AppScaffoldingForm(Form):
    name = CharField(max_length=80, label=_('App name'),
                     validators=[validate_id],
                     help_text=_('The app name must be camel case e.g. MyApp'))
    platform = ChoiceField(choices=versions, required=True,
                           label=_('Nextcloud version'))
    author_name = CharField(max_length=80, label=_('Author\'s full name'))
    author_email = EmailField(label=_('Author\'s E-Mail'))
    author_homepage = URLField(label=_('Author\'s homepage'), required=False)
    summary = CharField(max_length=256, label=_('Summary'), help_text=_(
        'Short description of your app that will be rendered as short teaser'))
    description = CharField(widget=Textarea, label=_('Description'),
                            help_text=_('Full description of what your app '
                                        'does. Can contain Markdown.'))
