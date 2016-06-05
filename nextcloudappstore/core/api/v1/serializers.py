from nextcloudappstore.core.models import App
from rest_framework import serializers


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
