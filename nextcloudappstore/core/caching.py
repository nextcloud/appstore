import datetime
from typing import Any

from django.db.models import Max, QuerySet
from semantic_version import Version

from nextcloudappstore.core.models import (
    App,
    AppRating,
    AppRatingDeleteLog,
    AppReleaseDeleteLog,
    Category,
    NextcloudRelease,
)


def create_etag(pairs: list[tuple[QuerySet, str]]) -> str:
    """
    Turn a list of queryset and timestamp pairs into an etag. The latest
    timestamp will be chosen as the etag
    :param pairs: a list of queryset and attribute which holds a timestamp
    :return: an etag
    """
    result = map(lambda p: p[0].aggregate(m=Max(p[1]))["m"], pairs)
    result = filter(lambda r: r is not None, result)
    return str(max(result, default=""))


def get_last_modified(pairs: list[tuple[QuerySet, str]]) -> datetime.datetime | None:
    result = map(lambda p: p[0].aggregate(m=Max(p[1]))["m"], pairs)
    result = filter(lambda r: r is not None, result)
    return max(result, default=None)


def apps_etag(request: Any, version: str) -> str:
    return create_etag(
        [
            (App.objects.all(), "last_release"),
            (AppReleaseDeleteLog.objects.all(), "last_modified"),
        ]
    )


def apps_last_modified(request: Any, version: str) -> datetime.datetime | None:
    return get_last_modified(
        [
            (App.objects.all(), "last_release"),
            (AppReleaseDeleteLog.objects.all(), "last_modified"),
        ]
    )


def apps_all_etag(request: Any) -> str:
    return create_etag(
        [
            (App.objects.all(), "last_release"),
            (AppReleaseDeleteLog.objects.all(), "last_modified"),
        ]
    )


def apps_all_last_modified(request: Any) -> datetime.datetime | None:
    return get_last_modified(
        [
            (App.objects.all(), "last_release"),
            (AppReleaseDeleteLog.objects.all(), "last_modified"),
        ]
    )


def app_etag(request: Any, id: str) -> str:
    return str(App.objects.get(id=id).last_modified)


def app_rating_etag(request: Any, id: str) -> str:
    return create_etag(
        [
            (AppRating.objects.filter(app__id=id), "last_modified"),
            (AppRatingDeleteLog.objects.all(), "last_modified"),
        ]
    )


def categories_etag(request: Any) -> str:
    return create_etag([(Category.objects.all(), "last_modified")])


def categories_last_modified(request: Any) -> datetime.datetime | None:
    return get_last_modified([(Category.objects.all(), "last_modified")])


def app_ratings_etag(request: Any) -> str:
    return create_etag([(AppRating.objects.all(), "last_modified")])


def nextcloud_release_etag(request: Any) -> str:
    releases = [Version(rel.version) for rel in NextcloudRelease.objects.all()]
    release_num = len(releases)
    latest_release = str(max(releases)) if release_num > 0 else ""
    return "%d-%s" % (release_num, latest_release)
