from django.test import TestCase
from nextcloudappstore.core.rating import compute_rating


class RatingTest(TestCase):
    """
    Floating point comparisons are dangerous but it seems to work fine (tm)
    """

    def test_below_threshold_rating(self):
        result = compute_rating([1.0], 1)
        self.assertEqual(0.5, result)

    def test_simple_rating(self):
        result = compute_rating([1.0], 0)
        self.assertEqual(1.0, result)

    def test_no_ratings(self):
        result = compute_rating([], -1)
        self.assertEqual(0.5, result)

    def test_full_rating(self):
        result = compute_rating([1.0, 1.0, 0.5, 0.5], 1)
        self.assertEqual(0.75, result)
