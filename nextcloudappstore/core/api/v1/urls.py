from django.conf.urls import url
from nextcloudappstore.core.api.v1.views import Apps, AppReleases

urlpatterns = [
    url(r'^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json$', Apps.as_view(),
        name='apps'),
    url(r'^apps/(?P<app>[a-z_]+)/(?P<version>\d+\.\d+\.\d+)/?$',
        AppReleases.as_view(), name='app-release-delete'),
    url(r'^apps/(?P<pk>[a-z_]+)/?$', Apps.as_view(), name='app-delete'),
]
