"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class SetDefaultAdminPasswordCommandTest(TestCase):
    fixtures = [
        "admin.json",
    ]

    def test_set_password(self):
        user = get_user_model().objects.get(username="admin")
        user.set_password("different")
        user.save()
        call_command("setdefaultadminpassword", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("admin"))
