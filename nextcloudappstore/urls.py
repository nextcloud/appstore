"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from allauth.account.views import signup
from allauth.socialaccount.views import signup as social_signup
from csp.decorators import csp_update
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path
from django.views.decorators.http import etag

from nextcloudappstore.core.caching import app_rating_etag
from nextcloudappstore.core.feeds import AppReleaseAtomFeed, AppReleaseRssFeed
from nextcloudappstore.core.views import (
    AppDetailView,
    AppRatingApi,
    AppRegisterView,
    AppReleasesView,
    AppUploadView,
    CategoryAppListView,
    app_description,
)
from nextcloudappstore.scaffolding.views import (
    AppScaffoldingView,
    IntegrationScaffoldingView,
)

admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path("", CategoryAppListView.as_view(), {"id": None}, name="home"),
    path("featured", CategoryAppListView.as_view(), {"id": None, "is_featured_category": True}, name="featured"),
    path("signup/", csp_update(**settings.CSP_SIGNUP)(signup), name="account_signup"),
    path("social/signup/", csp_update(**settings.CSP_SIGNUP)(social_signup), name="socialaccount_signup"),
    path("", include("allauth.urls")),
    re_path(r"^categories/(?P<id>[\w]*)/?$", CategoryAppListView.as_view(), name="category-app-list"),
    re_path(r"^developer/apps/generate/?$", AppScaffoldingView.as_view(), name="app-scaffold"),
    re_path(r"^developer/integration/new/?$", IntegrationScaffoldingView.as_view(), name="integration-scaffold"),
    re_path(r"^developer/apps/releases/new/?$", AppUploadView.as_view(), name="app-upload"),
    re_path(r"^developer/apps/new/?$", AppRegisterView.as_view(), name="app-register"),
    re_path(r"^apps/(?P<id>[\w_]+)/?$", AppDetailView.as_view(), name="app-detail"),
    re_path(r"^apps/(?P<id>[\w_]+)/releases/?$", AppReleasesView.as_view(), name="app-releases"),
    re_path(r"^apps/(?P<id>[\w_]+)/description/?$", app_description, name="app-description"),
    re_path(r"^apps/(?P<id>[\w_]+)/ratings.json$", etag(app_rating_etag)(AppRatingApi.as_view()), name="app-ratings"),
    path("api/", include("nextcloudappstore.api.urls", namespace="api")),
    path("account/", include("nextcloudappstore.user.urls", namespace="user")),
    re_path(r"^admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("captcha/", include("captcha.urls")),
]

urlpatterns += i18n_patterns(
    re_path(r"feeds/releases.rss", AppReleaseRssFeed(), name="feeds-releases-rss"),
    re_path(r"feeds/releases.atom", AppReleaseAtomFeed(), name="feeds-releases-atom"),
)

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
