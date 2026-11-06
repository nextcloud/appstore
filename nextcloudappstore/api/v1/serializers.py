"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from collections import defaultdict
from functools import cmp_to_key

from django.contrib.auth import get_user_model
from django.db.models.manager import BaseManager
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from rest_framework.fields import DateTimeField, SerializerMethodField

from nextcloudappstore.core.models import (
    App,
    AppApiEnvironmentVariable,
    AppApiReleaseApiScope,
    AppApiReleaseDeployMethod,
    AppAuthor,
    AppRating,
    AppRelease,
    Category,
    DatabaseDependency,
    NextcloudRelease,
    PhpExtensionDependency,
    Screenshot,
    Video,
)
from nextcloudappstore.core.validators import HttpsUrlValidator
from nextcloudappstore.core.versioning import php_version_compare


class PhpExtensionDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="php_extension.id")
    version_spec = SerializerMethodField()
    raw_version_spec = SerializerMethodField()

    class Meta:
        model = PhpExtensionDependency
        fields = ("id", "version_spec", "raw_version_spec")

    def get_version_spec(self, obj):
        return obj.version_spec.replace(",", " ")

    def get_raw_version_spec(self, obj):
        return obj.raw_version_spec.replace(",", " ")


class DatabaseDependencySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="database.id")
    version_spec = SerializerMethodField()
    raw_version_spec = SerializerMethodField()

    class Meta:
        model = DatabaseDependency
        fields = ("id", "version_spec", "raw_version_spec")

    def get_version_spec(self, obj):
        return obj.version_spec.replace(",", " ")

    def get_raw_version_spec(self, obj):
        return obj.raw_version_spec.replace(",", " ")


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ("id", "translations")


class NextcloudReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextcloudRelease
        fields = ("has_release", "version", "is_supported")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppAuthor
        fields = ("name", "mail", "homepage")


class AppReleaseSerializer(serializers.ModelSerializer):
    databases = DatabaseDependencySerializer(many=True, read_only=True, source="databasedependencies")
    php_extensions = PhpExtensionDependencySerializer(many=True, read_only=True, source="phpextensiondependencies")
    php_version_spec = SerializerMethodField()
    platform_version_spec = SerializerMethodField()
    raw_php_version_spec = SerializerMethodField()
    raw_platform_version_spec = SerializerMethodField()
    translations = TranslatedFieldsField(shared_model=AppRelease)

    class Meta:
        model = AppRelease
        fields = (
            "version",
            "php_extensions",
            "databases",
            "shell_commands",
            "php_version_spec",
            "platform_version_spec",
            "min_int_size",
            "download",
            "created",
            "licenses",
            "last_modified",
            "is_nightly",
            "raw_php_version_spec",
            "raw_platform_version_spec",
            "signature",
            "translations",
            "signature_digest",
        )

    def get_platform_version_spec(self, obj):
        return obj.platform_version_spec.replace(",", " ")

    def get_php_version_spec(self, obj):
        return obj.php_version_spec.replace(",", " ")

    def get_raw_platform_version_spec(self, obj):
        return obj.raw_platform_version_spec.replace(",", " ")

    def get_raw_php_version_spec(self, obj):
        return obj.raw_php_version_spec.replace(",", " ")


class DeployMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppApiReleaseDeployMethod
        fields = ("install_type", "install_data")


class ApiScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppApiReleaseApiScope
        fields = ("scope_name",)


class AppApiEnvironmentVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppApiEnvironmentVariable
        fields = ("env_name", "display_name", "description", "default")


class AppApiAppReleaseSerializer(AppReleaseSerializer):
    deploy_methods = DeployMethodSerializer(many=True, read_only=True)
    api_scopes = ApiScopeSerializer(many=True, read_only=True)
    environment_variables = AppApiEnvironmentVariableSerializer(many=True, read_only=True)

    class Meta:
        model = AppRelease
        fields = (
            "version",
            "php_extensions",
            "databases",
            "shell_commands",
            "php_version_spec",
            "platform_version_spec",
            "min_int_size",
            "download",
            "created",
            "licenses",
            "last_modified",
            "is_nightly",
            "raw_php_version_spec",
            "raw_platform_version_spec",
            "signature",
            "translations",
            "signature_digest",
            "aa_is_system",
            "deploy_methods",
            "api_scopes",
            "environment_variables",
        )


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ("url", "small_thumbnail")


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("url",)


class AppSerializer(serializers.ModelSerializer):
    releases = AppReleaseSerializer(many=True, read_only=True)
    discussion = SerializerMethodField()
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=App)
    last_modified = DateTimeField(source="last_release")

    class Meta:
        model = App
        fields = (
            "id",
            "categories",
            "user_docs",
            "admin_docs",
            "developer_docs",
            "issue_tracker",
            "website",
            "created",
            "last_modified",
            "releases",
            "screenshots",
            "videos",
            "translations",
            "is_featured",
            "authors",
            "rating_recent",
            "rating_overall",
            "rating_num_recent",
            "rating_num_overall",
            "certificate",
            "discussion",
        )

    def get_discussion(self, obj):
        return obj.discussion_url


class NewestReleasesSerializer(serializers.ListSerializer):
    """
    Lists only the releases a Nextcloud server can pick. A server filters an app's releases on their raw platform and
    PHP version specs, nightly flag and whether the version is a pre-release, then installs the highest version left
    according to PHP's version_compare(). Of releases that agree on those four values, only the highest can be picked.

    A set with a version ending in a character other than an ASCII letter or digit is kept whole: PHP before 8.4.22
    and 8.5.7 orders such versions inconsistently, so which one a server picks depends on how it sorts.
    """

    def to_representation(self, data):
        releases = list(data.all() if isinstance(data, BaseManager) else data)
        groups = defaultdict(list)
        for release in releases:
            groups[self._group(release)].append(release)
        selectable = set()
        for group in groups.values():
            if not all(self._ends_in_letter_or_digit(release.version) for release in group):
                selectable.update(id(release) for release in group)
                continue
            newest = max(group, key=cmp_to_key(lambda a, b: php_version_compare(a.version, b.version)))
            selectable.update(
                id(release) for release in group if php_version_compare(release.version, newest.version) == 0
            )
        return super().to_representation([release for release in releases if id(release) in selectable])

    @staticmethod
    def _ends_in_letter_or_digit(version):
        return version[-1:].isascii() and version[-1:].isalnum()

    @staticmethod
    def _group(release):
        return (
            release.raw_platform_version_spec,
            release.raw_php_version_spec,
            release.is_nightly,
            "-" in release.version,
        )


class AppWithNewestReleasesSerializer(AppSerializer):
    releases = NewestReleasesSerializer(child=AppReleaseSerializer(), read_only=True)


class AppApiAppSerializer(AppSerializer):
    releases = AppApiAppReleaseSerializer(many=True, read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name")


class AppRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    translations = TranslatedFieldsField(shared_model=AppRating)

    class Meta:
        model = AppRating
        fields = ("rating", "rated_at", "last_modified", "translations", "user", "app")


class AppReleaseDownloadSerializer(serializers.Serializer):
    download = serializers.URLField(validators=[HttpsUrlValidator()])
    signature = serializers.CharField()
    nightly = serializers.BooleanField(required=False, default=False)


class AppRegisterSerializer(serializers.Serializer):
    certificate = serializers.CharField()
    signature = serializers.CharField()
    is_enterprise_only = serializers.BooleanField(required=False, default=False)
