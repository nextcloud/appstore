import datetime
from typing import List

from nextcloudappstore.core.models import AppRating


def compute_app_rating(app_id: str, days: int = 90,
                       threshold: int = 10) -> float:
    """
    Computes an app rating based on
    :param app_id: the app id of the app whose rating should be computed
    :param days: passing 30 will only consider ratings from the last 30 days,
     pass a negative number to include all ratings
    :param threshold: if the amount of ratings is lower than this number
    return 0.5
    :return: the app rating
    """
    app_ratings = AppRating.objects.filter(app__id=app_id)
    if days >= 0:
        range = datetime.datetime.today() - datetime.timedelta(days=days)
        app_ratings = app_ratings.filter(rated_at__gte=range)
    ratings = map(lambda r: r.rating, app_ratings)
    return compute_rating(list(ratings), threshold)


def compute_rating(ratings: List[float], threshold: int = 10) -> float:
    """
    Turns a list of ratings into a score, 0 being the lowest and 1 being the
    highest. The idea is that everyone can use his own custom scale, e.g.
    a 5 star rating would multiply the value by 5. Also a too low number of
    ratings will default to a constant value.
    :param ratings: list of floats from 0 to 1
    :param threshold: if the amount of ratings is lower than this number
    return 0.5
    :return: the score
    """
    num_ratings = len(ratings)
    if threshold < num_ratings and num_ratings > 0:
        return sum(ratings) / num_ratings
    else:
        return 0.5
