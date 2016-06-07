from nextcloudappstore.core.models import *
from rest_framework import serializers


class PhpExtensionDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='php_extension.id')

    class Meta:
        model = PhpExtensionDependency
        fields = ('id', 'version_min', 'version_max')


class DatabaseDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='database.id')
    name = serializers.ReadOnlyField(source='database.name')

    class Meta:
        model = DatabaseDependency
        fields = ('id', 'name', 'version_min', 'version_max')


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
                                             source='databasedependency_set')
    libs = PhpExtensionDependencySerializer(many=True, read_only=True,
                                            source='phpextensiondependency_set')

    class Meta:
        model = AppRelease
        fields = ('version', 'libs', 'databases', 'shell_commands', 'php_min',
                  'php_max', 'platform_min', 'platform_max', 'int_size_min',
                  'download', 'created', 'last_modified')


class AppSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    releases = AppReleaseSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = App
        fields = ('id', 'categories', 'name', 'description', 'user_docs',
                  'admin_docs', 'developer_docs', 'issue_tracker', 'website',
                  'created', 'last_modified', 'releases', 'authors')
