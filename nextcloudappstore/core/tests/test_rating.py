from django.contrib.auth import get_user_model
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRating
from nextcloudappstore.core.rating import compute_rating


class RatingTest(TestCase):
    """
    Floating point comparisons are dangerous but it seems to work fine (tm)
    """

    def test_below_threshold_rating(self):
        result, num = compute_rating([1.0], 2)
        self.assertEqual(0.5, result)
        self.assertEqual(0, num)

    def test_simple_rating(self):
        result, num = compute_rating([1.0], 0)
        self.assertEqual(1.0, result)
        self.assertEqual(1, num)

    def test_no_ratings(self):
        result, num = compute_rating([], -1)
        self.assertEqual(0.5, result)
        self.assertEqual(0, num)

    def test_full_rating(self):
        result, num = compute_rating([1.0, 1.0, 0.5, 0.5], 1)
        self.assertEqual(0.75, result)
        self.assertEqual(4, num)

    def test_app_rating_save(self):
        user1 = self.create_user(1)
        user2 = self.create_user(2)
        user3 = self.create_user(3)
        user4 = self.create_user(4)
        app = App.objects.create(id="news", owner=user1)
        AppRating.objects.create(app=app, user=user1, rating=0.5)
        AppRating.objects.create(app=app, user=user2, rating=0.5)
        AppRating.objects.create(app=app, user=user3, rating=0.5)
        AppRating.objects.create(app=app, user=user4, rating=1.0)

        self.assertEqual(4, len(AppRating.objects.all()))
        self.assertEqual(0.5, App.objects.get(id=app.id).rating_overall)
        self.assertEqual(0, App.objects.get(id=app.id).rating_num_overall)
        self.assertEqual(0.5, App.objects.get(id=app.id).rating_recent)
        self.assertEqual(0, App.objects.get(id=app.id).rating_num_recent)

        user5 = self.create_user(5)
        AppRating.objects.create(app=app, user=user5, rating=1.0)

        self.assertEqual(5, len(AppRating.objects.all()))
        self.assertEqual(0.7, App.objects.get(id=app.id).rating_overall)
        self.assertEqual(5, App.objects.get(id=app.id).rating_num_overall)
        self.assertEqual(0.7, App.objects.get(id=app.id).rating_recent)
        self.assertEqual(5, App.objects.get(id=app.id).rating_num_recent)

    def create_user(self, id):
        user_id = "test%i" % id
        return get_user_model().objects.create_user(username=user_id, password=user_id, email=f"{user_id}@test.com")
