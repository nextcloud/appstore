"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from nextcloudappstore.core.models import App, AppRating
from nextcloudappstore.core.views import REPLY_MAX_LENGTH


class AppRatingReplyTest(TestCase):
    def setUp(self):
        self.owner = self.create_user("owner")
        self.rater = self.create_user("rater")
        self.other = self.create_user("other")
        self.app = App.objects.create(id="news", owner=self.owner)
        self.rating = AppRating.objects.create(app=self.app, user=self.rater, rating=0.0)
        self.rating.set_current_language("en")
        self.rating.comment = "Crashes on upload"
        self.rating.save()

    def create_user(self, name, **kwargs):
        return get_user_model().objects.create_user(username=name, password=name, email=f"{name}@example.com", **kwargs)

    def post_reply(self, user, reply, app=None, comment_id=None):
        if user is not None:
            self.client.force_login(user)
        return self.client.post(
            reverse("app-detail", kwargs={"id": (app or self.app).id}),
            data=json.dumps({"comment_id": comment_id or self.rating.id, "reply": reply}),
            content_type="application/json",
        )

    def reload(self):
        return AppRating.objects.get(pk=self.rating.pk)

    def test_owner_can_reply(self):
        self.post_reply(self.owner, "  Fixed in 2.1, thanks!  ")
        rating = self.reload()
        self.assertEqual("Fixed in 2.1, thanks!", rating.reply)
        self.assertIsNotNone(rating.replied_at)

    def test_owner_can_edit_reply(self):
        self.post_reply(self.owner, "First")
        self.post_reply(self.owner, "Second")
        self.assertEqual("Second", self.reload().reply)
        self.assertEqual(1, AppRating.objects.filter(app=self.app).count())

    def test_empty_reply_removes_it(self):
        self.post_reply(self.owner, "Fixed")
        self.post_reply(self.owner, "   ")
        rating = self.reload()
        self.assertEqual("", rating.reply)
        self.assertIsNone(rating.replied_at)

    def test_reply_bumps_last_modified(self):
        before = self.reload().last_modified
        self.post_reply(self.owner, "Fixed")
        self.assertGreater(self.reload().last_modified, before)

    def test_reply_keeps_comment_and_score(self):
        rating_overall = App.objects.get(pk=self.app.pk).rating_overall
        self.post_reply(self.owner, "Fixed")
        rating = self.reload()
        rating.set_current_language("en")
        self.assertEqual("Crashes on upload", rating.comment)
        self.assertEqual(0.0, rating.rating)
        self.assertEqual(rating_overall, App.objects.get(pk=self.app.pk).rating_overall)

    def test_rater_cannot_reply(self):
        self.post_reply(self.rater, "Me again")
        self.assertEqual("", self.reload().reply)

    def test_other_user_cannot_reply(self):
        self.post_reply(self.other, "Not my app")
        self.assertEqual("", self.reload().reply)

    def test_admin_who_is_not_owner_cannot_reply(self):
        admin = self.create_user("admin", is_superuser=True, is_staff=True)
        self.post_reply(admin, "Admin reply")
        self.assertEqual("", self.reload().reply)

    def test_co_maintainer_cannot_reply(self):
        self.app.co_maintainers.add(self.other)
        self.post_reply(self.other, "Co-maintainer reply")
        self.assertEqual("", self.reload().reply)

    def test_anonymous_cannot_reply(self):
        self.post_reply(None, "Anonymous")
        self.assertEqual("", self.reload().reply)

    def test_owner_cannot_reply_through_another_app(self):
        own_app = App.objects.create(id="owned", owner=self.other)
        foreign_app = App.objects.create(id="foreign", owner=self.owner)
        foreign_rating = AppRating.objects.create(app=foreign_app, user=self.rater, rating=1.0)
        # comment of "foreign" (owned by self.owner) sent via the URL of "owned"
        self.post_reply(self.other, "Wrong app", app=own_app, comment_id=foreign_rating.id)
        self.assertEqual("", AppRating.objects.get(pk=foreign_rating.pk).reply)

    def test_reply_to_unknown_comment_creates_nothing(self):
        count = AppRating.objects.count()
        self.post_reply(self.owner, "Hello", comment_id=999999)
        self.assertEqual(count, AppRating.objects.count())

    def test_too_long_reply_is_rejected(self):
        self.post_reply(self.owner, "x" * (REPLY_MAX_LENGTH + 1))
        self.assertEqual("", self.reload().reply)

    def test_reply_is_in_ratings_json(self):
        self.post_reply(self.owner, "Fixed in 2.1")
        self.client.logout()
        response = self.client.get(reverse("app-ratings", kwargs={"id": self.app.id}), {"lang": "en"})
        data = response.json()
        self.assertEqual(1, len(data))
        self.assertEqual("Fixed in 2.1", data[0]["reply"])
        self.assertIsNotNone(data[0]["repliedAt"])
        self.assertNotEqual("", data[0]["relativeRepliedAt"])

    def test_reply_label_names_the_owner(self):
        self.owner.first_name = "Jane"
        self.owner.last_name = "Doe"
        self.owner.save()
        response = self.client.get(reverse("app-detail", kwargs={"id": self.app.id}))
        self.assertContains(response, "Reply from Jane Doe (app owner)")

    def test_reply_label_falls_back_without_owner_name(self):
        response = self.client.get(reverse("app-detail", kwargs={"id": self.app.id}))
        self.assertContains(response, "Reply from the app owner")
