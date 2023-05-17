from django.conf.urls import include, url

app_name = "api"

urlpatterns = [
    url(r"^v1/", include("nextcloudappstore.api.v1.urls", namespace="v1")),
]
