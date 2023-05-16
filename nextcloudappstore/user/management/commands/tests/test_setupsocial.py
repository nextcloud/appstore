from io import StringIO

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import TestCase


class SetupSocialCommandTest(TestCase):
    def test_setup(self):
        call_command('setupsocial', '--github-secret=tres',
                     '--github-client-id=sec', '--domain=local.com',
                     stdout=StringIO())
        site = Site.objects.all()[0]
        app = SocialApp.objects.get(provider='github')

        self.assertEqual('local.com', site.domain)
        self.assertEqual('Nextcloud App Store', site.name)

        self.assertEqual('GitHub', app.name)
        self.assertEqual('tres', app.secret)
        self.assertEqual('sec', app.client_id)
