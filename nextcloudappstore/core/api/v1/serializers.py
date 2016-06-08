from nextcloudappstore.core.models import *
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


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name', 'mail', 'homepage')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class AppReleaseSerializer(serializers.ModelSerializer):
    databases = DatabaseDependencySerializer(many=True, read_only=True,
                                             source='databasedependencies')
    libs = PhpExtensionDependencySerializer(many=True, read_only=True,
                                            source='phpextensiondependencies')

    class Meta:
        model = AppRelease
        fields = (
            'version', 'libs', 'databases', 'shell_commands',
            'php_min_version', 'php_max_version', 'platform_min_version',
            'platform_max_version', 'min_int_size', 'download', 'created',
            'last_modified'
        )


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('url',)


class AppSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    releases = AppReleaseSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)

    class Meta:
        model = App
        fields = ('id', 'categories', 'name', 'description', 'user_docs',
                  'admin_docs', 'developer_docs', 'issue_tracker', 'website',
                  'created', 'last_modified', 'releases', 'authors',
                  'screenshots')
