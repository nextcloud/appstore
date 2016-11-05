from typing import List, Tuple

Rating = Tuple[float, int]


def compute_rating(ratings: List[float], threshold: int = 5) -> Rating:
    """
    Turns a list of ratings into a score, 0 being the lowest and 1 being the
    highest. The idea is that everyone can use his own custom scale, e.g.
    a 5 star rating would multiply the value by 5. Also a too low number of
    ratings will default to a constant value.
    :param ratings: list of floats from 0 to 1
    :param threshold: only calculate the rating if the amount of ratings is
     higher than or equal to the threshold number, otherwise return 0.5
    :return: a tuple with the score and number of ratings
    """
    num_ratings = len(ratings)
    threshold_num_ratings = threshold <= num_ratings
    if num_ratings > 0 and threshold_num_ratings:
        return (sum(ratings) / num_ratings, num_ratings)
    else:
        return (0.5, 0)
