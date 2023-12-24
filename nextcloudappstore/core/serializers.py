from django.contrib.humanize.templatetags.humanize import naturaltime
from parler_rest.fields import TranslatedFieldsField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from nextcloudappstore.api.v1.serializers import UserSerializer
from nextcloudappstore.core.models import AppRating


class AppRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    translations = TranslatedFieldsField(shared_model=AppRating)
    relative_rated_at = SerializerMethodField()

    class Meta:
        model = AppRating
        fields = ("id", "rating", "rated_at", "translations", "user", "app", "relative_rated_at", "appeal")

    def get_relative_rated_at(self, obj):
        return naturaltime(obj.rated_at)
