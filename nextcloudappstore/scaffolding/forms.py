import re
from os import listdir

from django.core.exceptions import ValidationError
from django.forms import Textarea, Form, URLField, MultipleChoiceField, \
    TextInput
from django.utils.translation import ugettext_lazy as _  # type: ignore
from django.forms.fields import EmailField, CharField, ChoiceField

from nextcloudappstore.core.facades import resolve_file_relative_path
from nextcloudappstore.core.models import Category
from django.utils.functional import lazy


def get_categories():
    return [(cat.id, cat.name) for cat in Category.objects.all()]


def get_versions():
    tpls = listdir(resolve_file_relative_path(__file__, 'app-templates'))
    return sorted(((v, v) for v in tpls))


def validate_id(input: str) -> None:
    regex = r'^([A-Z][a-z]*)+$'
    if not re.match(regex, input):
        raise ValidationError(_('The app name must be camel case e.g. MyApp'))


class AppScaffoldingForm(Form):
    name = CharField(max_length=80, label=_('App name'),
                     validators=[validate_id],
                     widget=TextInput(attrs={'placeholder': 'The app name '
                                                            'must be camel '
                                                            'case e.g. '
                                                            'MyApp'}))
    platform = ChoiceField(choices=lazy(get_versions, list), required=True,
                           label=_('Nextcloud version'))
    author_name = CharField(max_length=80, label=_('Author\'s full name'))
    author_email = EmailField(label=_('Author\'s e-mail'))
    author_homepage = URLField(label=_('Author\'s homepage'), required=False)
    issue_tracker = URLField(label=_('Issue tracker URL'), required=True,
                             help_text=_('Bug reports and feature requests'))
    categories = MultipleChoiceField(required=True, label=_('Categories'),
                                     choices=lazy(get_categories, list),
                                     help_text=_('Hold down Ctrl and click to '
                                                 'select multiple entries'))
    summary = CharField(max_length=256, label=_('Summary'), help_text=_(
        'Short description of your app that will be rendered as short teaser'))
    description = CharField(widget=Textarea, label=_('Description'),
                            help_text=_('Full description of what your app '
                                        'does. Can contain Markdown.'))
