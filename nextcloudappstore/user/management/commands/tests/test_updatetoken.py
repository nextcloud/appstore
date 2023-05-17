from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework.authtoken.models import Token

from nextcloudappstore.user.facades import create_user


class UpdateTokenCommandTest(TestCase):
    def test_update_token(self):
        user = create_user("cmdtest", "cmdtest", "cmdtest@test.com")
        call_command("updatetoken", "--username=cmdtest", "--token=token", stdout=StringIO())
        token = Token.objects.get(user=user)
        self.assertEqual("token", token.key)
