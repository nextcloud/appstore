from typing import List


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
