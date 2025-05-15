"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from io import StringIO

from allauth.account.models import EmailAddress
from django.core.management import call_command
from django.test import TestCase

from nextcloudappstore.user.facades import create_user


class VerifyEmailCommandTest(TestCase):
    def test_verify(self):
        mail = "cmdtest@test.com"
        username = "cmdtest"
        user = create_user(username, username, mail, False)

        with self.assertRaises(EmailAddress.DoesNotExist):
            EmailAddress.objects.get(user=user, email=mail)

        call_command("verifyemail", "--username=cmdtest", "--email=cmdtest@test.com", stdout=StringIO())

        email = EmailAddress.objects.get(user=user, email=mail)
        self.assertTrue(email.verified)
