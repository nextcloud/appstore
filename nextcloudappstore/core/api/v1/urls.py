from django.conf.urls import url
from nextcloudappstore.core.api.v1.views import Apps

urlpatterns = [
    url(r'^platform/(?P<version>\d+\.\d+\.\d+)/apps\.json', Apps.as_view(),
        name='apps'),
    url(r'^apps/(?P<pk>[a-z_]+)', Apps.as_view(), name='app-delete'),
]
