from django.contrib.auth import get_user_model
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from rest_framework.fields import DateTimeField, SerializerMethodField

from nextcloudappstore.core.models import (App, AppAuthor, AppRating,
                                           AppRelease, Category,
                                           DatabaseDependency, NextcloudRelease,
                                           PhpExtensionDependency, Screenshot)
from nextcloudappstore.core.validators import HttpsUrlValidator


class PhpExtensionDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='php_extension.id')
    version_spec = SerializerMethodField()
    raw_version_spec = SerializerMethodField()

    class Meta:
        model = PhpExtensionDependency
        fields = ('id', 'version_spec', 'raw_version_spec')

    def get_version_spec(self, obj):
        return obj.version_spec.replace(',', ' ')

    def get_raw_version_spec(self, obj):
        return obj.raw_version_spec.replace(',', ' ')


class DatabaseDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='database.id')
    version_spec = SerializerMethodField()
    raw_version_spec = SerializerMethodField()

    class Meta:
        model = DatabaseDependency
        fields = ('id', 'version_spec', 'raw_version_spec')

    def get_version_spec(self, obj):
        return obj.version_spec.replace(',', ' ')

    def get_raw_version_spec(self, obj):
        return obj.raw_version_spec.replace(',', ' ')


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ('id', 'translations')


class NextcloudReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextcloudRelease
        fields = ('has_release', 'version', 'is_supported')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppAuthor
        fields = ('name', 'mail', 'homepage')


class AppReleaseSerializer(serializers.ModelSerializer):
    databases = DatabaseDependencySerializer(many=True, read_only=True,
                                             source='databasedependencies')
    php_extensions = \
        PhpExtensionDependencySerializer(many=True, read_only=True,
                                         source='phpextensiondependencies')
    php_version_spec = SerializerMethodField()
    platform_version_spec = SerializerMethodField()
    raw_php_version_spec = SerializerMethodField()
    raw_platform_version_spec = SerializerMethodField()
    translations = TranslatedFieldsField(shared_model=AppRelease)

    class Meta:
        model = AppRelease
        fields = (
            'version', 'php_extensions', 'databases', 'shell_commands',
            'php_version_spec', 'platform_version_spec', 'min_int_size',
            'download', 'created', 'licenses', 'last_modified', 'is_nightly',
            'raw_php_version_spec', 'raw_platform_version_spec', 'signature',
            'translations', 'signature_digest'
        )

    def get_platform_version_spec(self, obj):
        return obj.platform_version_spec.replace(',', ' ')

    def get_php_version_spec(self, obj):
        return obj.php_version_spec.replace(',', ' ')

    def get_raw_platform_version_spec(self, obj):
        return obj.raw_platform_version_spec.replace(',', ' ')

    def get_raw_php_version_spec(self, obj):
        return obj.raw_php_version_spec.replace(',', ' ')


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('url', 'small_thumbnail')


class AppSerializer(serializers.ModelSerializer):
    releases = AppReleaseSerializer(many=True, read_only=True)
    discussion = SerializerMethodField()
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=App)
    last_modified = DateTimeField(source='last_release')

    class Meta:
        model = App
        fields = (
            'id', 'categories', 'user_docs', 'admin_docs', 'developer_docs',
            'issue_tracker', 'website', 'created', 'last_modified', 'releases',
            'screenshots', 'translations', 'is_featured', 'authors',
            'rating_recent', 'rating_overall', 'rating_num_recent',
            'rating_num_overall', 'certificate', 'discussion'
        )

    def get_discussion(self, obj):
        return obj.discussion_url


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name')


class AppRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    translations = TranslatedFieldsField(shared_model=AppRating)

    class Meta:
        model = AppRating
        fields = ('rating', 'rated_at', 'translations', 'user', 'app')


class AppReleaseDownloadSerializer(serializers.Serializer):
    download = serializers.URLField(validators=[HttpsUrlValidator()])
    signature = serializers.CharField()
    nightly = serializers.BooleanField(required=False, default=False)


class AppRegisterSerializer(serializers.Serializer):
    certificate = serializers.CharField()
    signature = serializers.CharField()
