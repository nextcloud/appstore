"""
SPDX-FileCopyrightText: 2018 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime
from urllib.request import Request

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from nextcloudappstore.core.caching import (
    app_ratings_etag,
    apps_all_etag,
    apps_all_last_modified,
    categories_etag,
    nextcloud_release_etag,
)
from nextcloudappstore.core.models import App, AppRating, Category, NextcloudRelease


class CachingTest(TestCase):
    def test_cache_nextcloud_release_etag_empty(self):
        etag = nextcloud_release_etag(Request("https://"))
        self.assertEqual("0-", etag)

    def test_cache_nextcloud_release_etag(self):
        NextcloudRelease.objects.create(version="12.0.2")
        NextcloudRelease.objects.create(version="12.0.1")

        etag = nextcloud_release_etag(Request("https://"))
        self.assertEqual("2-12.0.2", etag)

    def test_categories_etag(self):
        category = Category.objects.create(pk="test")
        etag = categories_etag(Request("https://"))
        self.assertEqual(str(category.last_modified), etag)

    def test_app_ratings_etag(self):
        user = User.objects.create(username="hi")
        app = App.objects.create(id="test", owner=user)
        rating = AppRating.objects.create(app=app, user=user)

        etag = app_ratings_etag(Request("https://"))
        self.assertEqual(str(rating.last_modified), etag)


class AppsAllCachingTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="hi")
        self.t1 = timezone.now()
        self.app = App.objects.create(id="news", owner=self.user, last_release=self.t1)

    def _request(self, include_enterprise=None):
        data = {"include_enterprise": include_enterprise} if include_enterprise is not None else {}
        return self.factory.get("/apps.json", data)

    def test_etag_excludes_enterprise_only_apps_by_default(self):
        t2 = self.t1 + datetime.timedelta(hours=1)
        App.objects.create(id="ent", owner=self.user, is_enterprise_only=True, last_release=t2)

        default_etag = apps_all_etag(self._request())
        self.assertEqual(str(self.t1), default_etag)

    def test_etag_includes_enterprise_only_apps_when_requested(self):
        t2 = self.t1 + datetime.timedelta(hours=1)
        App.objects.create(id="ent", owner=self.user, is_enterprise_only=True, last_release=t2)

        enterprise_etag = apps_all_etag(self._request("true"))
        self.assertEqual(str(t2), enterprise_etag)

    def test_enterprise_app_change_does_not_bust_default_etag(self):
        default_before = apps_all_etag(self._request())
        enterprise_before = apps_all_etag(self._request("true"))

        t2 = self.t1 + datetime.timedelta(hours=1)
        App.objects.create(id="ent", owner=self.user, is_enterprise_only=True, last_release=t2)

        default_after = apps_all_etag(self._request())
        enterprise_after = apps_all_etag(self._request("true"))

        self.assertEqual(default_before, default_after)
        self.assertNotEqual(enterprise_before, enterprise_after)

    def test_non_enterprise_app_change_busts_both_etags(self):
        default_before = apps_all_etag(self._request())
        enterprise_before = apps_all_etag(self._request("true"))

        t2 = self.t1 + datetime.timedelta(hours=1)
        self.app.last_release = t2
        self.app.save()

        default_after = apps_all_etag(self._request())
        enterprise_after = apps_all_etag(self._request("true"))

        self.assertNotEqual(default_before, default_after)
        self.assertNotEqual(enterprise_before, enterprise_after)

    def test_last_modified_excludes_enterprise_only_apps_by_default(self):
        t2 = self.t1 + datetime.timedelta(hours=1)
        App.objects.create(id="ent", owner=self.user, is_enterprise_only=True, last_release=t2)

        self.assertEqual(self.t1, apps_all_last_modified(self._request()))

    def test_last_modified_includes_enterprise_only_apps_when_requested(self):
        t2 = self.t1 + datetime.timedelta(hours=1)
        App.objects.create(id="ent", owner=self.user, is_enterprise_only=True, last_release=t2)

        self.assertEqual(t2, apps_all_last_modified(self._request("true")))
