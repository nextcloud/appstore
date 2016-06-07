from nextcloudappstore.core.models import App, AppRelease
from rest_framework import serializers


class AppReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppRelease
        fields = ('version', 'libs', 'databases', 'shell_commands', 'php_min',
                  'php_max', 'platform_min', 'platform_max', 'int_size_min',
                  'download', 'created', 'last_modified')


class AppSerializer(serializers.ModelSerializer):
    releases = AppReleaseSerializer(many=True, read_only=True)

    class Meta:
        model = App
        fields = ('id', 'categories', 'name', 'description', 'user_docs',
                  'admin_docs', 'developer_docs', 'issue_tracker', 'website',
                  'created', 'last_modified', 'releases')
