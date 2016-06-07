from nextcloudappstore.core.api.v1.mixins import ListDestroyAPIView
from nextcloudappstore.core.api.v1.serializers import AppSerializer
from nextcloudappstore.core.models import App
from nextcloudappstore.core.permissions import AllowedToEditApp
from rest_framework import authentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class Apps(ListDestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, AllowedToEditApp)
    serializer_class = AppSerializer
    queryset = App.objects.all()


class AppReleases(GenericAPIView):
    pass
