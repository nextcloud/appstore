from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("v1/", include("nextcloudappstore.api.v1.urls", namespace="v1")),
]
