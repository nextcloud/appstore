from django.conf.urls import url
from django.views.decorators.http import etag
from nextcloudappstore.core.api.v1.views import Apps, AppReleases, \
    app_api_etag, Categories, category_api_etag

urlpatterns = [
    url(r'^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$',
        etag(app_api_etag)(Apps.as_view()), name='apps'),
    url(r'^apps/releases/?$', AppReleases.as_view(),
        name='app-release-create'),
    url(r'^apps/(?P<pk>[a-z_]+)/?$', Apps.as_view(), name='app-delete'),
    url(r'^apps/(?P<app>[a-z_]+)/releases/(?P<version>\d+\.\d+\.\d+'
        r'(?:-nightly)?)/?$',
        AppReleases.as_view(), name='app-release-delete'),
    url(r'^categories.json$',
        etag(category_api_etag)(Categories.as_view()), name='categories'),
]
