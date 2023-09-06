from django.urls import re_path
from django.views.decorators.http import etag

from nextcloudappstore.api.v1.views import (
    AppRatingView,
    AppRegisterView,
    AppReleaseView,
    AppsView,
    AppView,
    CategoryView,
    NextcloudReleaseView,
    RegenerateAuthToken,
    SessionObtainAuthToken,
)
from nextcloudappstore.core.caching import (
    app_ratings_etag,
    apps_all_etag,
    apps_etag,
    categories_etag,
    nextcloud_release_etag,
)
from nextcloudappstore.core.versioning import SEMVER_REGEX

app_name = "v1"

urlpatterns = [
    re_path(r"^platforms\.json$", etag(nextcloud_release_etag)(NextcloudReleaseView.as_view()), name="platforms"),
    re_path(r"^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$", etag(apps_etag)(AppView.as_view()), name="app"),
    re_path(r"^apps\.json$", etag(apps_all_etag)(AppsView.as_view()), name="apps"),
    re_path(r"^apps/releases/?$", AppReleaseView.as_view(), name="app-release-create"),
    re_path(r"^apps/?$", AppRegisterView.as_view(), name="app-register"),
    re_path(r"^apps/(?P<pk>[a-z0-9_]+)/?$", AppView.as_view(), name="app-delete"),
    re_path(r"^ratings.json$", etag(app_ratings_etag)(AppRatingView.as_view()), name="app-ratings"),
    re_path(
        r"^apps/(?P<app>[a-z0-9_]+)/releases/(?:(?P<nightly>nightly)/)?" r"(?P<version>" + SEMVER_REGEX + ")/?$",
        AppReleaseView.as_view(),
        name="app-release-delete",
    ),
    re_path(r"^token/?$", SessionObtainAuthToken.as_view(), name="user-token"),
    re_path(r"^token/new/?$", RegenerateAuthToken.as_view(), name="user-token-new"),
    re_path(r"^categories.json$", etag(categories_etag)(CategoryView.as_view()), name="category"),
]
