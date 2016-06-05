from nextcloudappstore.api.serializers import AppSerializer
from nextcloudappstore.core.models import App
from rest_framework.response import Response
from rest_framework.views import APIView


class Apps(APIView):
    def get(self, request, version):
        apps = App.objects.all()
        serializer = AppSerializer(apps, many=True)
        return Response(serializer.data)
