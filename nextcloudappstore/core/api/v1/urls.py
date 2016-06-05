from django.conf.urls import url
from nextcloudappstore.core.api.v1.views import Apps

urlpatterns = [
    url(r'^platform/(?P<version>\d+(\.\d)*)/apps\.json', Apps.as_view()),
]
