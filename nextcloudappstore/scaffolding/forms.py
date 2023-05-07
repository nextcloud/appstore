import re
from os import listdir
import uuid

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.forms import Textarea, Form, URLField, MultipleChoiceField, \
    TextInput, BooleanField
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _  # type: ignore
from django.forms.fields import EmailField, CharField, ChoiceField,\
    HiddenInput

from nextcloudappstore.core.facades import resolve_file_relative_path
from nextcloudappstore.core.models import App, Category, Screenshot
from django.utils.functional import lazy


def get_categories():
    return [(cat.id, cat.name) for cat in Category.objects.all()]


def get_versions():
    tpls = listdir(resolve_file_relative_path(__file__, 'app-templates'))
    return sorted(((v, v) for v in tpls), reverse=True)


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
    author_email = EmailField(label=_('Author\'s email'), required=True)
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
    opt_in = BooleanField(
        label=_('I opt in for the collection of my personal data. '
                'We could then reach out to you to check in with you about '
                'your plans or to ask for feedback on our developer program.'),
        required=False)


class IntegrationScaffoldingForm(Form):
    name = CharField(max_length=80, label=_('Integration name'),
                     widget=TextInput())
    author_homepage = URLField(label=_('Author\'s homepage'), required=False)
    issue_tracker = URLField(label=_('Issue tracker URL'), required=False,
                             help_text=_('Bug reports and feature requests'))
    categories = MultipleChoiceField(widget=HiddenInput(), disabled=True,
                                     required=True, label=_('Categories'),
                                     choices=lazy(get_categories, list),
                                     help_text=_('Hold down Ctrl and click to '
                                                 'select multiple entries'))
    summary = CharField(max_length=256, label=_('Summary'), help_text=_(
        'Short description of your app that will be rendered as short teaser'))
    screenshot = URLField(max_length=256, label=_('Screenshot URL'),
                          required=False,
                          help_text=_('URL for integration screenshot'))
    screenshot_thumbnail = URLField(max_length=256, label=_('Screenshot '
                                                            'thumbnail URL'),
                                    required=False,
                                    help_text=_('URL for integration '
                                                'screenshot in '
                                                'smaller dimensions. '
                                                'Must be used in combination '
                                                'with a larger screenshot.'))
    description = CharField(widget=Textarea, label=_('Description'),
                            help_text=_('Full description of what your'
                                        ' integration '
                                        'does. Can contain Markdown.'))

    def _create_discourse_category(self, app_id: str) -> None:
        url = '%s/categories?api_key=%s&api_username=%s' % (
            settings.DISCOURSE_URL.rstrip('/'),
            settings.DISCOURSE_TOKEN,
            settings.DISCOURSE_USER
        )
        data = {
            'name': app_id.replace('_', '-'),
            'color': '3c3945',
            'text_color': 'ffffff'
        }
        if settings.DISCOURSE_PARENT_CATEGORY_ID:
            data['parent_category_id'] = settings.DISCOURSE_PARENT_CATEGORY_ID

        # ignore requests errors because there can be many issues and we do not
        # want to abort app registration just because the forum is down or
        # leak sensitive data like tokens or users
        try:
            requests.post(url, data=data, timeout=30)
        except requests.HTTPError:
            pass

    def save(self, user, app_id, action):
        if app_id is None:
            app_id = slugify(self.cleaned_data['name']).replace('-', '_')[:80]
        try:
            app = App.objects.get(id=app_id)
            if app.can_update(user) or user.is_superuser:
                if action == "reject" and user.is_superuser:
                    '''Not optimal but works'''
                    Screenshot.objects.filter(app=app).delete()
                    app.delete()
                elif action == "approve" and user.is_superuser:
                    app.approved = True
                    if settings.DISCOURSE_TOKEN:
                        self._create_discourse_category(app_id)
                    app.save()
                    return app_id
                else:
                    '''Not optimal but works'''
                    Screenshot.objects.filter(app=app).delete()
                    if self.data['screenshot']:
                        screenshot = Screenshot.objects.create(
                            url=self.cleaned_data['screenshot'],
                            small_thumbnail=self.cleaned_data[
                                'screenshot_thumbnail'],
                            ordering=1, app=app)
                        screenshot.save()

                    app.description = self.cleaned_data['description']
                    app.name = self.cleaned_data['name']
                    app.summary = self.cleaned_data['summary']
                    app.website = self.cleaned_data['author_homepage']
                    app.issue_tracker = self.cleaned_data['issue_tracker']
                    app.save()
                    return app_id
        except App.DoesNotExist:
            app = App.objects.create(id=app_id, owner=user,
                                     certificate=uuid.uuid1().urn)
            app.set_current_language('en')
            app.categories.set(self.cleaned_data['categories'])
            app.description = self.cleaned_data['description']
            app.name = self.cleaned_data['name']
            app.summary = self.cleaned_data['summary']
            app.website = self.cleaned_data['author_homepage']
            app.issue_tracker = self.cleaned_data['issue_tracker']
            app.save()
            p = App.objects.get(id=app_id)
            p.is_integration = True
            if user.is_superuser:
                p.approved = True
                if settings.DISCOURSE_TOKEN:
                    self._create_discourse_category(app_id)
            else:
                send_mail("New integration submitted", "Please review the "
                                                       "integration to make "
                                                       "sure it fits the "
                                                       "guidelines.",
                          settings.NEXTCLOUD_FROM_EMAIL,
                          settings.NEXTCLOUD_INTEGRATIONS_APPROVAL_EMAILS)
            p.save()
            if self.data['screenshot']:
                screenshot = Screenshot.objects.create(
                    url=self.cleaned_data['screenshot'],
                    small_thumbnail=self.cleaned_data['screenshot_thumbnail'],
                    ordering=1, app=p)
                screenshot.save()
            if not p.is_integration or p.approved or user.is_superuser:
                return app_id
