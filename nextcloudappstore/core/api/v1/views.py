import requests
from django.db import transaction
from django.http import Http404
from django.conf import settings
from requests import HTTPError
from pymple import Container
from rest_framework import authentication, parsers, renderers  # type: ignore
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import DestroyAPIView, \
    get_object_or_404, ListAPIView  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied

from nextcloudappstore.core.api.v1.release.importer import AppImporter
from nextcloudappstore.core.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.core.api.v1.serializers import AppSerializer, \
    AppReleaseDownloadSerializer, CategorySerializer, AppRatingSerializer, \
    AppRegisterSerializer
from nextcloudappstore.core.certificate.validator import CertificateValidator
from nextcloudappstore.core.facades import read_file_contents
from nextcloudappstore.core.models import App, AppRelease, Category, AppRating
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.throttling import PostThrottle


class CategoryView(ListAPIView):
    queryset = Category.objects.prefetch_related('translations').all()
    serializer_class = CategorySerializer


class AppRatingView(ListAPIView):
    queryset = AppRating.objects.all()
    serializer_class = AppRatingSerializer


class AppView(DestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        version = self.kwargs['version']
        working_apps = App.objects.get_compatible(version)
        serializer = self.get_serializer(working_apps, many=True,
                                         version=version)
        return Response(serializer.data)


class AppRegisterView(APIView):
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_classes = (PostThrottle,)
    throttle_scope = 'app_register'

    def post(self, request):
        serializer = AppRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signature = serializer.validated_data['signature'].strip()
        certificate = serializer.validated_data['certificate'].strip()

        container = Container()

        # validate certificate and signature
        chain = read_file_contents(settings.NEXTCLOUD_CERTIFICATE_LOCATION)
        crl = read_file_contents(settings.NEXTCLOUD_CRL_LOCATION)
        validator = container.resolve(CertificateValidator)
        app_id = validator.get_cn(certificate)
        if settings.VALIDATE_CERTIFICATES:
            validator.validate_certificate(certificate, chain, crl)
            validator.validate_signature(certificate, signature,
                                         app_id.encode())

        try:
            app = App.objects.get(id=app_id)
            if app.ownership_transfer_enabled:
                app.owner = request.user
                app.ownership_transfer_enabled = False
            elif app.owner != request.user:
                msg = 'Only the app owner is allowed to update the certificate'
                raise PermissionDenied(msg)
            app.certificate = certificate
            app.save()
            return Response(status=204)
        except App.DoesNotExist:
            app = App.objects.create(id=app_id, owner=request.user,
                                     certificate=certificate)
            app.set_current_language('en')
            app.description = app_id
            app.name = app_id
            app.summary = app_id
            app.save()
            if settings.DISCOURSE_TOKEN:
                self._create_discourse_category(app_id)
            return Response(status=201)

    def _create_discourse_category(self, app_id: str) -> None:
        url = '%s/categories?api_key=%s&api_username=%s' % (
            settings.DISCOURSE_URL.rstrip('/'),
            settings.DISCOURSE_TOKEN,
            settings.DISCOURSE_USER
        )
        data = {
            'name': app_id,
            'color': '3c3945',
            'text_color': 'ffffff'
        }
        if settings.DISCOURSE_PARENT_CATEGORY_ID:
            data['parent_category_id'] = settings.DISCOURSE_PARENT_CATEGORY_ID

        # ignore requests errors because there can be many issues and we do not
        # want to abort app registration just because the forum is down or
        # leak sensitive data like tokens or users
        try:
            requests.post(url, data=data)
        except requests.HTTPError:
            pass


class AppReleaseView(DestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission, IsAuthenticated)
    throttle_classes = (PostThrottle,)
    throttle_scope = 'app_upload'

    def post(self, request):
        serializer = AppReleaseDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with(transaction.atomic()):
            url = serializer.validated_data['download']
            signature = serializer.validated_data['signature']
            is_nightly = serializer.validated_data['nightly']

            # download the latest release and create or update the models
            container = Container()
            provider = container.resolve(AppReleaseProvider)
            try:
                info, data = provider.get_release_info(url, is_nightly)
            except HTTPError as e:
                raise ValidationError(e)

            # populate metadata from request
            info['app']['release']['signature'] = signature
            info['app']['release']['download'] = url

            app_id = info['app']['id']
            version = info['app']['release']['version']

            status, app = self._check_permission(request, app_id, version,
                                                 is_nightly)

            # verify certs and signature
            validator = container.resolve(CertificateValidator)
            chain = read_file_contents(settings.NEXTCLOUD_CERTIFICATE_LOCATION)
            crl = read_file_contents(settings.NEXTCLOUD_CRL_LOCATION)
            if settings.VALIDATE_CERTIFICATES:
                validator.validate_certificate(app.certificate, chain, crl)
                validator.validate_signature(app.certificate, signature, data)
                validator.validate_app_id(app.certificate, app_id)

            importer = container.resolve(AppImporter)
            importer.import_data('app', info['app'], None)
        return Response(status=status)

    def _check_permission(self, request, app_id, version, is_nightly):
        try:
            app = App.objects.get(pk=app_id)
        except App.DoesNotExist:
            raise ValidationError('App %s does not exist, you need to register'
                                  'it first' % app_id)

        # if an app release does not exist, it must be checked if the
        # user is allowed to create it first
        try:
            release = AppRelease.objects.filter(version=version, app=app,
                                                is_nightly=is_nightly)
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
        is_nightly = self.kwargs['nightly'] is not None
        release = AppRelease.objects.filter(version=self.kwargs['version'],
                                            app__id=self.kwargs['app'],
                                            is_nightly=is_nightly)
        release = get_object_or_404(release)
        self.check_object_permissions(self.request, release)
        return release


class SessionObtainAuthToken(APIView):
    """Modified version of rest_framework.authtoken.views.ObtainAuthToken.

    Modified to return token based on SessionAuthentication, and not just data
    sent for BasicAuthentication.
    """

    authentication_classes = (authentication.SessionAuthentication,
                              authentication.BasicAuthentication,)
    throttle_classes = (PostThrottle,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser,
                      parsers.MultiPartParser,
                      parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key})


class RegenerateAuthToken(APIView):
    """Generates a new API token for the authenticated user, regardless of
    whether a token already exists.

    Accepts TokenAuthentication and BasicAuthentication.
    """

    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    throttle_classes = (PostThrottle,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser,
                      parsers.MultiPartParser,
                      parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            Token.objects.get(user=request.user).delete()
        except Exception:
            pass
        new = Token.objects.create(user=request.user)
        return Response({'token': new.key})
