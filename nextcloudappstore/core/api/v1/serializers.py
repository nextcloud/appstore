from nextcloudappstore.core.models import *
from nextcloudappstore.core.validators import HttpsUrlValidator
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers


class PhpExtensionDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='php_extension.id')

    class Meta:
        model = PhpExtensionDependency
        fields = ('id', 'min_version', 'max_version')


class DatabaseDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='database.id')
    name = serializers.ReadOnlyField(source='database.name')

    class Meta:
        model = DatabaseDependency
        fields = ('id', 'name', 'min_version', 'max_version')


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ('id', 'name')


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ('id', 'name')


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ('id', 'translations')


class AppReleaseSerializer(serializers.ModelSerializer):
    databases = DatabaseDependencySerializer(many=True, read_only=True,
                                             source='databasedependencies')
    php_extensions = \
        PhpExtensionDependencySerializer(many=True, read_only=True,
                                         source='phpextensiondependencies')
    licenses = LicenseSerializer(many=True, read_only=True)

    class Meta:
        model = AppRelease
        fields = (
            'version', 'php_extensions', 'databases', 'shell_commands',
            'php_min_version', 'php_max_version', 'platform_min_version',
            'platform_max_version', 'min_int_size', 'download', 'created',
            'licenses', 'last_modified', 'checksum'
        )


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('url',)


class AppSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    releases = AppReleaseSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=App)
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = App
        fields = (
            'id', 'categories', 'user_docs', 'admin_docs', 'developer_docs',
            'issue_tracker', 'website', 'created', 'last_modified', 'releases',
            'screenshots', 'translations', 'recommendations'
        )

    def get_recommendations(self, obj):
        return obj.recommendations.count()


class AppReleaseDownloadSerializer(serializers.Serializer):
    download = serializers.URLField(validators=[HttpsUrlValidator()])
    checksum = serializers.CharField(max_length=64, min_length=64,
                                     required=False)
