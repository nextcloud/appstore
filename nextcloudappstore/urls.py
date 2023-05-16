from allauth.account.views import signup
from allauth.socialaccount.views import signup as social_signup
from csp.decorators import csp_update
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.decorators.http import etag

from nextcloudappstore.core.caching import app_rating_etag
from nextcloudappstore.core.feeds import AppReleaseAtomFeed, AppReleaseRssFeed
from nextcloudappstore.core.views import (AppDetailView, AppRatingApi,
                                          AppRegisterView, AppReleasesView,
                                          AppUploadView, CategoryAppListView,
                                          app_description)
from nextcloudappstore.scaffolding.views import (AppScaffoldingView,
                                                 IntegrationScaffoldingView)

admin.site.login = login_required(admin.site.login)

urlpatterns = [
    url(r'^$', CategoryAppListView.as_view(), {'id': None}, name='home'),
    url(r"^featured$", CategoryAppListView.as_view(), {'id': None,
                                                       'is_featured_category':
                                                           True},
        name='featured'),
    url(r"^signup/$", csp_update(**settings.CSP_SIGNUP)(signup),
        name="account_signup"),
    url(r"^social/signup/$", csp_update(**settings.CSP_SIGNUP)(social_signup),
        name="socialaccount_signup"),
    url(r'^', include('allauth.urls')),
    url(r'^categories/(?P<id>[\w]*)/?$', CategoryAppListView.as_view(),
        name='category-app-list'),
    url(r'^developer/apps/generate/?$', AppScaffoldingView.as_view(),
        name='app-scaffold'),
    url(r'^developer/integration/new/?$', IntegrationScaffoldingView.as_view(),
        name='integration-scaffold'),
    url(r'^developer/apps/releases/new/?$', AppUploadView.as_view(),
        name='app-upload'),
    url(r'^developer/apps/new/?$', AppRegisterView.as_view(),
        name='app-register'),
    url(r'^apps/(?P<id>[\w_]+)/?$', AppDetailView.as_view(),
        name='app-detail'),
    url(r'^apps/(?P<id>[\w_]+)/releases/?$', AppReleasesView.as_view(),
        name='app-releases'),
    url(r'^apps/(?P<id>[\w_]+)/description/?$', app_description,
        name='app-description'),
    url(r'^apps/(?P<id>[\w_]+)/ratings.json$',
        etag(app_rating_etag)(AppRatingApi.as_view()), name='app-ratings'),
    url(r'^api/', include('nextcloudappstore.api.urls',
                          namespace='api')),
    url(r'^account/',
        include('nextcloudappstore.user.urls', namespace='user')),
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
]

urlpatterns += i18n_patterns(
    url(r'feeds/releases.rss', AppReleaseRssFeed(), name='feeds-releases-rss'),
    url(r'feeds/releases.atom', AppReleaseAtomFeed(),
        name='feeds-releases-atom'),
)

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
    except ImportError:
        pass
