"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import json
import os
from collections import defaultdict
from functools import cmp_to_key

import requests
from django.conf import settings
from django.db import connection, transaction
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.gzip import gzip_page
from jschon import JSON, JSONSchema, create_catalog
from pymple import Container
from requests import HTTPError
from rest_framework import authentication, parsers, renderers  # type: ignore
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.generics import (  # type: ignore
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView

from nextcloudappstore.api.v1.release.importer import AppImporter
from nextcloudappstore.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.api.v1.serializers import (
    AppApiAppSerializer,
    AppRatingSerializer,
    AppRegisterSerializer,
    AppReleaseDownloadSerializer,
    AppSerializer,
    AppSubmitSerializer,
    CategorySerializer,
    NextcloudReleaseSerializer,
)
from nextcloudappstore.certificate.validator import CertificateValidator
from nextcloudappstore.core.enterprise import enterprise_enabled, filter_enterprise
from nextcloudappstore.core.facades import read_file_contents
from nextcloudappstore.core.github import (
    AppCertificateExistsError,
    GitHubClient,
    create_app_certificate_request_pr,
    get_download_counts,
)
from nextcloudappstore.core.models import (
    App,
    AppRating,
    AppRelease,
    Category,
    NextcloudRelease,
)
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.throttling import PostThrottle
from nextcloudappstore.core.versioning import php_version_compare, version_in_spec
from nextcloudappstore.user.facades import update_token

BASIC_PREFETCH_LIST = [
    "authors",
    "screenshots",
    "videos",
    "categories",
    "translations",
]

RELEASES_PREFETCH_LIST = [
    "releases__translations",
    "releases__phpextensiondependencies__php_extension",
    "releases__databasedependencies__database",
    "releases__shell_commands",
    "releases__licenses",
]

APP_PREFETCH_LIST = [
    *BASIC_PREFETCH_LIST,
    Prefetch("releases", queryset=AppRelease.objects.filter(Q(aa_is_system__isnull=True))),
    *RELEASES_PREFETCH_LIST,
]

AA_APP_PREFETCH_LIST = [
    *BASIC_PREFETCH_LIST,
    Prefetch("releases", queryset=AppRelease.objects.filter(Q(aa_is_system__isnull=False))),
    *RELEASES_PREFETCH_LIST,
    "releases__deploy_methods",
    "releases__api_scopes",
    "releases__environment_variables",
]


def selectable_release_ids() -> list[int]:
    """
    Ids of the releases a Nextcloud server can pick, which apps.json lists for the apps a request may see. A server
    filters an app's releases on their raw platform and PHP version specs, nightly flag and whether the version is a
    pre-release, then installs the highest version left according to PHP's version_compare(). Of releases that agree
    on those four values, only the highest can be picked.

    A set with a version ending in a character other than an ASCII letter or digit is kept whole: PHP before 8.4.22
    and 8.5.7 orders such versions inconsistently, so which one a server picks depends on how it sorts.
    """
    groups = defaultdict(list)
    releases = (
        AppRelease.objects.filter(aa_is_system__isnull=True)
        .order_by()
        .values_list("id", "app_id", "version", "raw_platform_version_spec", "raw_php_version_spec", "is_nightly")
    )
    for release_id, app_id, version, platform_spec, php_spec, is_nightly in releases:
        groups[app_id, platform_spec, php_spec, is_nightly, "-" in version].append((release_id, version))
    ids = []
    for group in groups.values():
        if not all(version[-1:].isascii() and version[-1:].isalnum() for _, version in group):
            ids.extend(release_id for release_id, _ in group)
            continue
        newest = max((version for _, version in group), key=cmp_to_key(php_version_compare))
        ids.extend(release_id for release_id, version in group if php_version_compare(version, newest) == 0)
    return ids


class EnterpriseFilterMixin:
    """Filter out enterprise-only apps unless a valid subscription key is provided."""

    def get_queryset(self):
        return filter_enterprise(super().get_queryset(), self.request)


class CategoryView(ListAPIView):
    queryset = Category.objects.prefetch_related("translations").all()
    serializer_class = CategorySerializer


class AppRatingView(ListAPIView):
    queryset = AppRating.objects.all()
    serializer_class = AppRatingSerializer


class NextcloudReleaseView(ListAPIView):
    queryset = NextcloudRelease.objects.all()
    serializer_class = NextcloudReleaseSerializer


@method_decorator(gzip_page, name="dispatch")
class AppsView(EnterpriseFilterMixin, ListAPIView):
    queryset = App.objects.annotate(
        num_releases=Count("releases", filter=Q(releases__aa_is_system__isnull=True))
    ).filter(Q(num_releases__gt=0) | Q(is_integration=True))
    serializer_class = AppSerializer

    def list(self, request, *args, **kwargs):
        # The release ids and the releases loaded for them must come from one snapshot, or a release replaced in
        # between is missing. PostgreSQL's default isolation gives each query its own snapshot. The isolation level
        # can only be set before a transaction's first query, so inside an existing transaction it stays as it is.
        snapshot = connection.vendor == "postgresql" and connection.get_autocommit()
        with transaction.atomic():
            if snapshot:
                with connection.cursor() as cursor:
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            return super().list(request, *args, **kwargs)

    @cached_property
    def release_ids(self):
        return selectable_release_ids()

    def get_queryset(self):
        # A stable and a nightly release can share a version. A server that accepts nightlies installs the first one
        # listed, so the stable one comes first.
        releases = AppRelease.objects.filter(id__in=self.release_ids).order_by("-version", "is_nightly")
        return (
            super()
            .get_queryset()
            .prefetch_related(*BASIC_PREFETCH_LIST, Prefetch("releases", queryset=releases), *RELEASES_PREFETCH_LIST)
        )


class AppApiAppsView(EnterpriseFilterMixin, ListAPIView):
    queryset = (
        App.objects.prefetch_related(*AA_APP_PREFETCH_LIST)
        .annotate(num_releases=Count("releases", filter=Q(releases__aa_is_system__isnull=False)))
        .filter(num_releases__gt=0)
    )
    serializer_class = AppApiAppSerializer


class PlatformAppsView(GenericAPIView):
    """Apps compatible with one Nextcloud version, served at platform/<version>/apps.json."""

    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        version = self.kwargs["version"]
        working_apps = App.objects.get_compatible(version, prefetch=APP_PREFETCH_LIST)
        if not enterprise_enabled(request):
            working_apps = [app for app in working_apps if not app.is_enterprise_only]
        serializer = self.get_serializer(working_apps, many=True)
        data = self._filter_releases(serializer.data, version)
        return Response(data)

    def _filter_releases(self, data, version):
        """
        Story time: this was once done in serializers but turned out to cause
        an extreme amount of queries. So we fetch everything by default and
        then filter out unneeded releases that dont match the version
        :param data: the serialized data
        :param version: the Nextcloud version that we filter
        :return: a filtered result set to be serialized
        """

        def is_compatible(release) -> bool:
            spec = release["platform_version_spec"].replace(" ", ",")
            return version_in_spec(version, spec)

        for app in data:
            app["releases"] = list(filter(is_compatible, app["releases"]))
        return data


class AppView(DestroyAPIView):
    """Deleting an app, at apps/<id>. DELETE only: DRF answers anything else with 405."""

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()


class AppSubmitView(APIView):
    """Submit an app CSR by opening a PR on the certificate-requests repo."""

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)
    throttle_classes = (PostThrottle,)
    throttle_scope = "app_register"

    def post(self, request):
        serializer = AppSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not settings.GITHUB_API_TOKEN:
            raise ValidationError("Certificate request submission is not configured")

        app_id = serializer.validated_data["app_id"]
        repository = serializer.validated_data["repository"]
        csr = serializer.validated_data["csr"].strip()
        client = GitHubClient(settings.GITHUB_API_BASE_URL, settings.GITHUB_API_TOKEN)
        try:
            pr_url = create_app_certificate_request_pr(
                client,
                settings.GITHUB_APP_CERTIFICATE_REPO,
                app_id,
                csr,
                repository,
                request.user.get_username(),
            )
        except AppCertificateExistsError as exc:
            raise ValidationError("An app with this id already has a certificate") from exc
        except requests.RequestException as exc:
            raise APIException("Could not create certificate request pull request") from exc

        return Response({"pull_request_url": pr_url}, status=201)


class AppRegisterView(APIView):
    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)
    throttle_classes = (PostThrottle,)
    throttle_scope = "app_register"

    def post(self, request):
        serializer = AppRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signature = serializer.validated_data["signature"].strip()
        certificate = serializer.validated_data["certificate"].strip()
        is_enterprise_only = serializer.validated_data["is_enterprise_only"]

        container = Container()

        # validate certificate and signature
        chain = read_file_contents(settings.NEXTCLOUD_CERTIFICATE_LOCATION)
        crl = read_file_contents(settings.NEXTCLOUD_CRL_LOCATION)
        validator = container.resolve(CertificateValidator)
        app_id = validator.get_cn(certificate)
        if settings.VALIDATE_CERTIFICATES:
            validator.validate_certificate(certificate, chain, crl)
            validator.validate_signature(certificate, signature, app_id.encode())

        try:
            app = App.objects.get(id=app_id)
            if app.ownership_transfer_enabled:
                app.owner = request.user
                app.ownership_transfer_enabled = False
                app.is_orphan = False
            elif app.owner != request.user:
                msg = "Only the app owner is allowed to update the certificate"
                raise PermissionDenied(msg)
            app.certificate = certificate
            app.save()
            return Response(status=204)
        except App.DoesNotExist:
            app = App.objects.create(
                id=app_id, owner=request.user, certificate=certificate, is_enterprise_only=is_enterprise_only
            )
            app.set_current_language("en")
            app.description = app_id
            app.name = app_id
            app.summary = app_id
            app.save()
            if settings.DISCOURSE_TOKEN:
                self._create_discourse_category(app_id)
            return Response(status=201)

    def _create_discourse_category(self, app_id: str) -> None:
        url = "{}/categories?api_key={}&api_username={}".format(
            settings.DISCOURSE_URL.rstrip("/"),
            settings.DISCOURSE_TOKEN,
            settings.DISCOURSE_USER,
        )
        data = {"name": app_id.replace("_", "-"), "color": "3c3945", "text_color": "ffffff"}
        if settings.DISCOURSE_PARENT_CATEGORY_ID:
            data["parent_category_id"] = settings.DISCOURSE_PARENT_CATEGORY_ID

        # ignore requests errors because there can be many issues and we do not
        # want to abort app registration just because the forum is down or
        # leak sensitive data like tokens or users
        try:
            requests.post(url, data=data, timeout=30)
        except requests.HTTPError:
            pass


class AppReleaseView(DestroyAPIView):
    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (UpdateDeletePermission, IsAuthenticated)
    throttle_classes = (PostThrottle,)
    throttle_scope = "app_upload"

    def post(self, request):
        serializer = AppReleaseDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            url = serializer.validated_data["download"]
            signature = serializer.validated_data["signature"]
            is_nightly = serializer.validated_data["nightly"]

            # download the latest release and create or update the models
            container = Container()
            provider = container.resolve(AppReleaseProvider)
            try:
                info, data = provider.get_release_info(url, is_nightly)
            except HTTPError as e:
                raise ValidationError(e)

            # populate metadata from request
            info["app"]["release"]["signature"] = signature
            info["app"]["release"]["download"] = url

            app_id = info["app"]["id"]
            version = info["app"]["release"]["version"]

            status, app = self._check_permission(request, app_id, version, is_nightly)

            # verify certs and signature
            validator = container.resolve(CertificateValidator)
            chain = read_file_contents(settings.NEXTCLOUD_CERTIFICATE_LOCATION)
            crl = read_file_contents(settings.NEXTCLOUD_CRL_LOCATION)
            if settings.VALIDATE_CERTIFICATES:
                validator.validate_certificate(app.certificate, chain, crl)
                validator.validate_signature(app.certificate, signature, data)
                validator.validate_app_id(app.certificate, app_id)

            importer = container.resolve(AppImporter)
            importer.import_data("app", info["app"], None)
        return Response(status=status)

    def _check_permission(self, request, app_id, version, is_nightly):
        try:
            app = App.objects.get(pk=app_id)
        except App.DoesNotExist:
            raise ValidationError(f"App {app_id} does not exist, you need to registerit first")

        # if an app release does not exist, it must be checked if the
        # user is allowed to create it first
        try:
            release = AppRelease.objects.filter(version=version, app=app, is_nightly=is_nightly)
            release = get_object_or_404(release)
            self.check_object_permissions(self.request, release)
            status = 200
        except Http404:
            release = AppRelease()
            release.version = version
            release.app = app
            release.is_nightly = is_nightly
            self.check_object_permissions(request, release)
            release.save()
            status = 201

        return status, app

    def get_object(self):
        if "nightly" in self.kwargs:
            is_nightly = self.kwargs["nightly"] is not None
        else:
            is_nightly = False
        release = AppRelease.objects.filter(
            version=self.kwargs["version"], app__id=self.kwargs["app"], is_nightly=is_nightly
        )
        release = get_object_or_404(release)
        self.check_object_permissions(self.request, release)
        return release


class SessionObtainAuthToken(APIView):
    """Modified version of rest_framework.authtoken.views.ObtainAuthToken.

    Modified to return token based on SessionAuthentication, and not just data
    sent for BasicAuthentication.
    """

    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    )
    throttle_classes = (PostThrottle,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({"token": token.key})


class RegenerateAuthToken(APIView):
    """Generates a new API token for the authenticated user, regardless of
    whether a token already exists.

    Accepts TokenAuthentication and BasicAuthentication.
    """

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    throttle_classes = (PostThrottle,)
    throttle_scope = "api_token_gen"

    permission_classes = (IsAuthenticated,)
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        return Response({"token": update_token(request.user.username).key})


class DiscoverView(APIView):
    discover_file = settings.DISCOVER_PATH
    throttle_classes = (PostThrottle,)
    throttle_scope = "discover_upload"
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return []

    def get(self, request, *args, **kwargs):
        if not os.path.exists(self.discover_file):
            return Response({"error": "File not found"}, status=404)

        file_response = FileResponse(open(self.discover_file, "rb"))
        return file_response

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file provided."}, status=400)

        catalog = create_catalog("2020-12")
        try:
            schema = JSONSchema.loadf(settings.DISCOVER_SCHEME, catalog=catalog)
        except OSError:
            return Response({"error": "Schema file not found."}, status=500)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON schema."}, status=500)

        new_discover_data = request.FILES["file"].read()
        result = schema.evaluate(JSON.loads(new_discover_data))
        if not result.valid:
            return Response({"errors": [error for error in result.output("detailed")["errors"]]}, status=400)

        try:
            with open(self.discover_file, "wb") as destination:
                destination.write(new_discover_data)
        except OSError:
            return Response({"error": "Unable to save file."}, status=500)
        return Response({"message": "File saved successfully"}, status=200)


class AppDownloadStatsView(APIView):
    """Return GitHub download counts for all releases of an app.

    Only the app owner and co-maintainers may access this endpoint.
    Releases not hosted on GitHub (or whose GitHub API call fails) have
    download_count set to null.
    """

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        app = get_object_or_404(App, pk=pk)
        if not app.can_update(request.user):
            raise PermissionDenied()
        releases = list(AppRelease.objects.filter(app=app).order_by("-last_modified"))
        client = GitHubClient(settings.GITHUB_API_BASE_URL, settings.GITHUB_API_TOKEN)
        return Response(get_download_counts(releases, client))
