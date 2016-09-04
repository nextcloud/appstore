from django.conf.urls import url
from django.views.decorators.http import etag
from nextcloudappstore.core.api.v1.views import AppView, AppReleaseView, \
    CategoryView, app_api_etag, category_api_etag, SessionObtainAuthToken, \
    RegenerateAuthToken, AppRatingView, app_rating_api_etag

urlpatterns = [
    url(r'^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$',
        etag(app_api_etag)(AppView.as_view()), name='app'),
    url(r'^apps/releases/?$', AppReleaseView.as_view(),
        name='app-release-create'),
    url(r'^apps/(?P<pk>[a-z_]+)/?$', AppView.as_view(), name='app-delete'),
    url(r'^apps/ratings.json$',
        etag(app_rating_api_etag)(AppRatingView.as_view()),
        name='app-ratings'),
    url(r'^apps/(?P<app>[a-z_]+)/releases/(?P<version>\d+\.\d+\.\d+'
        r'(?:-nightly)?)/?$',
        AppReleaseView.as_view(), name='app-release-delete'),
    url(r'^token/?$', SessionObtainAuthToken.as_view(), name='user-token'),
    url(r'^token/new/?$', RegenerateAuthToken.as_view(),
        name='user-token-new'),
    url(r'^categories.json$',
        etag(category_api_etag)(CategoryView.as_view()), name='category'),
]
