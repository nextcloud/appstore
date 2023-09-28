import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from pymple import Container
from requests import HTTPError
from rest_framework import authentication, parsers, renderers  # type: ignore
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import DestroyAPIView  # type: ignore
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated  # type: ignore
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
    CategorySerializer,
    NextcloudReleaseSerializer,
)
from nextcloudappstore.certificate.validator import CertificateValidator
from nextcloudappstore.core.facades import read_file_contents
from nextcloudappstore.core.models import (
    App,
    AppRating,
    AppRelease,
    Category,
    NextcloudRelease,
)
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.throttling import PostThrottle
from nextcloudappstore.core.versioning import version_in_spec
from nextcloudappstore.user.facades import update_token

BASIC_PREFETCH_LIST = [
    "authors",
    "screenshots",
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
    Prefetch("releases", queryset=AppRelease.objects.filter(Q(aa_proto__isnull=True) | Q(aa_proto=""))),
    *RELEASES_PREFETCH_LIST,
]

AA_APP_PREFETCH_LIST = [
    *BASIC_PREFETCH_LIST,
    Prefetch("releases", queryset=AppRelease.objects.filter(Q(aa_proto__isnull=False) & ~Q(aa_proto=""))),
    *RELEASES_PREFETCH_LIST,
    "releases__deploy_methods",
    "releases__api_scopes",
]


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
class AppsView(ListAPIView):
    queryset = (
        App.objects.prefetch_related(*APP_PREFETCH_LIST)
        .annotate(num_releases=Count("releases", filter=Q(releases__aa_proto__isnull=True) | Q(releases__aa_proto="")))
        .filter(Q(num_releases__gt=0) | Q(is_integration=True))
    )
    serializer_class = AppSerializer


class AppApiAppsView(ListAPIView):
    queryset = (
        App.objects.prefetch_related(*AA_APP_PREFETCH_LIST)
        .annotate(
            num_releases=Count("releases", filter=Q(releases__aa_proto__isnull=False) & ~Q(releases__aa_proto=""))
        )
        .filter(num_releases__gt=0)
    )
    serializer_class = AppApiAppSerializer


class AppView(DestroyAPIView):
    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
    )
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        version = self.kwargs["version"]
        working_apps = App.objects.get_compatible(version, prefetch=APP_PREFETCH_LIST)
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
            elif app.owner != request.user:
                msg = "Only the app owner is allowed to update the certificate"
                raise PermissionDenied(msg)
            app.certificate = certificate
            app.save()
            return Response(status=204)
        except App.DoesNotExist:
            app = App.objects.create(id=app_id, owner=request.user, certificate=certificate)
            app.set_current_language("en")
            app.description = app_id
            app.name = app_id
            app.summary = app_id
            app.save()
            if settings.DISCOURSE_TOKEN:
                self._create_discourse_category(app_id)
            return Response(status=201)

    def _create_discourse_category(self, app_id: str) -> None:
        url = "%s/categories?api_key=%s&api_username=%s" % (
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
            raise ValidationError("App %s does not exist, you need to registerit first" % app_id)

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
