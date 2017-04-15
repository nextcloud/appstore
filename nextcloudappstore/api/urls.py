from django.conf.urls import url, include

urlpatterns = [
    url(r'^v0/', include('nextcloudappstore.api.v0.urls',
                         namespace='v0')),
    url(r'^v1/', include('nextcloudappstore.api.v1.urls',
                         namespace='v1')),
]
