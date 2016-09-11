from django.db import transaction
from django.db.models import Max, Count
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
from rest_framework.exceptions import APIException, ValidationError

from nextcloudappstore.core.api.v1.release.importer import AppImporter
from nextcloudappstore.core.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.core.api.v1.serializers import AppSerializer, \
    AppReleaseDownloadSerializer, CategorySerializer, AppRatingSerializer
from nextcloudappstore.core.certificate.validator import CertificateValidator
from nextcloudappstore.core.facades import read_file_contents
from nextcloudappstore.core.models import App, AppRelease, Category, AppRating
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.throttling import PostThrottle


def app_api_etag(request, version):
    app_aggr = App.objects.aggregate(count=Count('*'),
                                     modified=Max('last_release'))
    release_aggr = AppRelease.objects.aggregate(count=Count('*'),
                                                modified=Max('last_modified'))
    release_modified = release_aggr['modified']
    app_modified = app_aggr['modified']
    count = '%i-%i' % (app_aggr['count'], release_aggr['count'])

    if app_modified is None and release_modified is None:
        return None
    elif app_modified is None:
        return '%s-%s' % (count, release_modified)
    elif release_modified is None:
        return '%s-%s' % (count, app_modified)
    else:
        if app_modified > release_modified:
            return '%s-%s' % (count, app_modified)
        else:
            return '%s-%s' % (count, release_modified)


def create_etag(queryset, modified_field='last_modified'):
    aggregate = queryset.aggregate(count=Count('*'),
                                   modified=Max(modified_field))
    modified = aggregate['modified']
    if modified is None:
        return None
    else:
        return '%s-%s' % (aggregate['count'], modified)


def category_api_etag(request):
    return create_etag(Category.objects.all())


def app_rating_api_etag(request):
    return create_etag(AppRating.objects.all(), 'rated_at')


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
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
        working_apps = App.objects.get_compatible(self.kwargs['version'])
        serializer = self.get_serializer(working_apps, many=True)
        return Response(serializer.data)


class AppRegisterView(APIView):
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission, IsAuthenticated)
    throttle_classes = (PostThrottle,)
    throttle_scope = 'app_register'

    def post(self, request):
        # TBD, also adjust permission classes
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
                info, data = provider.get_release_info(url)
            except HTTPError as e:
                raise APIException(e)

            # populate metadata from request
            if is_nightly:
                info['app']['release']['version'] += '-nightly'
            info['app']['release']['signature'] = signature
            info['app']['release']['download'] = url

            app_id = info['app']['id']
            version = info['app']['release']['version']

            status, app = self._check_permission(request, app_id, version)

            # verify certs and signature
            validator = container.resolve(CertificateValidator)
            chain = read_file_contents(settings.NEXTCLOUD_CERTIFICATE_LOCATION)
            crl = read_file_contents(settings.NEXTCLOUD_CRL_LOCATION)
            validator.validate_certificate(app.certificate, chain, crl)
            validator.validate_signature(app.certificate, signature, data)
            validator.validate_app_id(app.certificate, app_id)

            importer = container.resolve(AppImporter)
            importer.import_data('app', info['app'], None)
        return Response(status=status)

    def _check_permission(self, request, app_id, version):
        try:
            app = App.objects.get(pk=app_id)
        except App.DoesNotExist:
            raise ValidationError('App %s does not exist, you need to register'
                                  'it first' % app_id)

        # if an app release does not exist, it must be checked if the
        # user is allowed to create it first
        try:
            release = AppRelease.objects.filter(version=version, app=app)
            release = get_object_or_404(release)
            self.check_object_permissions(self.request, release)
            status = 200
        except Http404:
            release = AppRelease()
            release.version = version
            release.app = app
            self.check_object_permissions(request, release)
            release.save()
            status = 201

        return status, app

    def get_object(self):
        release = AppRelease.objects.filter(version=self.kwargs['version'],
                                            app__id=self.kwargs['app'])
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
        except:
            pass
        new = Token.objects.create(user=request.user)
        return Response({'token': new.key})
