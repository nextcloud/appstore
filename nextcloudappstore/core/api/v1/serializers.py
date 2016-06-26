from nextcloudappstore.core.models import *
from nextcloudappstore.core.validators import HttpsUrlValidator
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField


class PhpExtensionDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='php_extension.id')
    version_spec = SerializerMethodField()

    class Meta:
        model = PhpExtensionDependency
        fields = ('id', 'version_spec')

    def get_version_spec(self, obj):
        return obj.version_spec.replace(',', ' ')


class DatabaseDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='database.id')
    version_spec = SerializerMethodField()

    class Meta:
        model = DatabaseDependency
        fields = ('id', 'version_spec')

    def get_version_spec(self, obj):
        return obj.version_spec.replace(',', ' ')


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
    php_version_spec = SerializerMethodField()
    platform_version_spec = SerializerMethodField()

    class Meta:
        model = AppRelease
        fields = (
            'version', 'php_extensions', 'databases', 'shell_commands',
            'php_version_spec', 'platform_version_spec', 'min_int_size',
            'download', 'created', 'licenses', 'last_modified', 'checksum'
        )

    def get_platform_version_spec(self, obj):
        return obj.platform_version_spec.replace(',', ' ')

    def get_php_version_spec(self, obj):
        return obj.php_version_spec.replace(',', ' ')


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('url',)


class AppSerializer(serializers.ModelSerializer):
    releases = AppReleaseSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=App)
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = App
        fields = (
            'id', 'categories', 'user_docs', 'admin_docs', 'developer_docs',
            'issue_tracker', 'website', 'created', 'last_modified', 'releases',
            'screenshots', 'translations', 'recommendations', 'featured'
        )

    def get_recommendations(self, obj):
        return obj.recommendations.count()


class AppReleaseDownloadSerializer(serializers.Serializer):
    download = serializers.URLField(validators=[HttpsUrlValidator()])
    checksum = serializers.CharField(max_length=64, min_length=64,
                                     required=False)
