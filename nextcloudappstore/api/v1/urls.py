from django.conf.urls import url
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
    url(r"^platforms\.json$", etag(nextcloud_release_etag)(NextcloudReleaseView.as_view()), name="platforms"),
    url(r"^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$", etag(apps_etag)(AppView.as_view()), name="app"),
    url(r"^apps\.json$", etag(apps_all_etag)(AppsView.as_view()), name="apps"),
    url(r"^apps/releases/?$", AppReleaseView.as_view(), name="app-release-create"),
    url(r"^apps/?$", AppRegisterView.as_view(), name="app-register"),
    url(r"^apps/(?P<pk>[a-z0-9_]+)/?$", AppView.as_view(), name="app-delete"),
    url(r"^ratings.json$", etag(app_ratings_etag)(AppRatingView.as_view()), name="app-ratings"),
    url(
        r"^apps/(?P<app>[a-z0-9_]+)/releases/(?:(?P<nightly>nightly)/)?" r"(?P<version>" + SEMVER_REGEX + ")/?$",
        AppReleaseView.as_view(),
        name="app-release-delete",
    ),
    url(r"^token/?$", SessionObtainAuthToken.as_view(), name="user-token"),
    url(r"^token/new/?$", RegenerateAuthToken.as_view(), name="user-token-new"),
    url(r"^categories.json$", etag(categories_etag)(CategoryView.as_view()), name="category"),
]
