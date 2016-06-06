from nextcloudappstore.core.api.v1.mixins import ListDestroyAPIView
from nextcloudappstore.core.api.v1.serializers import AppSerializer
from nextcloudappstore.core.models import App
from rest_framework import authentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# TODO: crete permissions class which check if a user who wants to delete or
# modify an app is in the apps_appid group, e.g. apps_news. Maybe look into
# object permissions like django-guardian

class Apps(ListDestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AppSerializer
    queryset = App.objects.all()


class AppReleases(GenericAPIView):
    pass
