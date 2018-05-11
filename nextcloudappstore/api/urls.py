from django.conf.urls import url, include

app_name = 'api'

urlpatterns = [
    url(r'^v1/', include('nextcloudappstore.api.v1.urls', namespace='v1')),
]
