from django.conf.urls import url
from django.views.decorators.http import etag
from nextcloudappstore.core.api.v1.views import AppView, AppReleaseView, \
    CategoryView, SessionObtainAuthToken, RegenerateAuthToken, AppRatingView, \
    AppRegisterView
from nextcloudappstore.core.caching import app_ratings_etag, categories_etag, \
    apps_etag

urlpatterns = [
    url(r'^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$',
        etag(apps_etag)(AppView.as_view()), name='app'),
    url(r'^apps/releases/?$', AppReleaseView.as_view(),
        name='app-release-create'),
    url(r'^apps/?$', AppRegisterView.as_view(), name='app-register'),
    url(r'^apps/(?P<pk>[a-z_]+)/?$', AppView.as_view(), name='app-delete'),
    url(r'^ratings.json$',
        etag(app_ratings_etag)(AppRatingView.as_view()),
        name='app-ratings'),
    url(r'^apps/(?P<app>[a-z_]+)/releases/(?:(?P<is_nightly>nightly)/)?'
        r'(?P<version>\d+\.\d+\.\d+)/?$',
        AppReleaseView.as_view(), name='app-release-delete'),
    url(r'^token/?$', SessionObtainAuthToken.as_view(), name='user-token'),
    url(r'^token/new/?$', RegenerateAuthToken.as_view(),
        name='user-token-new'),
    url(r'^categories.json$',
        etag(categories_etag)(CategoryView.as_view()), name='category'),
]
