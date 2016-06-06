from nextcloudappstore.core.api.v1.mixins import ListDestroyAPIView
from nextcloudappstore.core.api.v1.serializers import AppSerializer
from nextcloudappstore.core.models import App
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class Apps(ListDestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AppSerializer
    queryset = App.objects.all()
