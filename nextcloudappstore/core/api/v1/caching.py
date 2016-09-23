from typing import List, Tuple
from django.db.models import Max, QuerySet
from nextcloudappstore.core.api.v1.models import AppReleaseDeleteLog
from nextcloudappstore.core.models import App, AppRelease, Category, AppRating


def create_etag(pairs: List[Tuple[QuerySet, str]]) -> str:
    """
    Turn a list of queryset and timestamp pairs into an etag. The latest
    timestamp will be chosen as the etag
    :param pairs: a list of queryset and attribute which holds a timestamp
    :return: an etag
    """
    result = map(lambda p: p[0].aggregate(m=Max(p[1]))['m'], pairs)
    result = filter(lambda r: r is not None, result)
    return str(max(result, default=''))


def app_etag(request, version: str) -> str:
    return create_etag([
        (App.objects.all(), 'last_release'),
        (AppReleaseDeleteLog.objects.all(), 'last_modified'),
    ])


def category_etag(request) -> str:
    return create_etag([(Category.objects.all(), 'last_modified')])


def app_rating_etag(request) -> str:
    return create_etag([(AppRating.objects.all(), 'rated_at')])
