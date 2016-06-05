from django.conf.urls import url
from nextcloudappstore.api.views import Apps

urlpatterns = [
    url(r'^platform/(?P<version>\d+(\.\d)*)/apps\.json', Apps.as_view()),
]
