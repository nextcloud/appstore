"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.contrib.auth.models import User
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRelease


class CertDeleteReleasesTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create(username="user", password="pass")
        self.app = App.objects.create(name="App", certificate="CERT1", owner=self.owner)
        self.rel1 = AppRelease.objects.create(version="1.0.0", app=self.app)
        self.rel2 = AppRelease.objects.create(version="2.0.0", app=self.app)
        self.rel3 = AppRelease.objects.create(version="3.0.0", app=self.app)
        self.rel4 = AppRelease.objects.create(version="4.0.0", app=self.app)

    def test_cert_has_changed(self):
        self.assertEqual(self.app.releases.count(), 4)
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "CERT2"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 0)

    def test_ignore_carriage_return(self):
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "CER\rT1"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 5)

    def test_ignore_start_end_spaces(self):
        AppRelease.objects.create(version="5.0.0", app=self.app)
        self.assertEqual(self.app.releases.count(), 5)
        self.app.certificate = "\n\nCER\rT1\n\n"
        self.app.save()
        self.assertEqual(self.app.releases.count(), 5)
