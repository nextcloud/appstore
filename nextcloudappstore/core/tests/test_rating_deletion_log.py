"""
SPDX-FileCopyrightText: 2023 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRating, AppRatingDeleteLog


class AppRatingDeletionLogTest(TestCase):
    def test_delete_app(self):
        user = get_user_model().objects.create(username="doe")
        app_rating = AppRating.objects.create(app=App.objects.create(owner=user, id="news"), user=user)
        self.assertEqual(0, AppRatingDeleteLog.objects.count())

        app_rating.delete()
        self.assertEqual(1, AppRatingDeleteLog.objects.count())

    def test_delete_owner(self):
        user = get_user_model().objects.create(username="doe")
        AppRating.objects.create(app=App.objects.create(owner=user, id="news"), user=user)
        self.assertEqual(0, AppRatingDeleteLog.objects.count())

        user.delete()
        self.assertEqual(1, AppRatingDeleteLog.objects.count())

    def test_delete_app_rating(self):
        user = get_user_model().objects.create(username="doe")
        app = App.objects.create(owner=user, id="news")
        app_rating = AppRating.objects.create(app=app, user=user)
        self.assertEqual(0, AppRatingDeleteLog.objects.count())
        app_rating.delete()

        self.assertEqual(1, AppRatingDeleteLog.objects.count())
