from django.db import transaction
from django.http import Http404
from nextcloudappstore.core.api.v1.release.importer import ReleaseImporter
from nextcloudappstore.core.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.core.api.v1.serializers import AppSerializer, \
    AppReleaseDownloadSerializer, CategorySerializer
from django.db.models import Max, Count
from nextcloudappstore.core.models import App, AppRelease, Category
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.throttling import PostThrottle
from pymple import Container
from rest_framework import authentication  # type: ignore
from rest_framework.generics import DestroyAPIView, \
    get_object_or_404, ListAPIView  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore
from semantic_version import Version, Spec


def app_api_etag(request, version):
    app_aggr = App.objects.aggregate(count=Count('*'),
                                     modified=Max('last_modified'))
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


def category_api_etag(request):
    category_aggr = Category.objects.aggregate(count=Count('*'),
                                               modified=Max('last_modified'))
    category_modified = category_aggr['modified']
    if category_modified is None:
        return None
    else:
        return '%s-%s' % (category_aggr['count'], category_modified)


class Categories(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class Apps(DestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,
                              authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        apps = App.objects.prefetch_related('translations', 'screenshots',
                                            'releases', 'releases__databases',
                                            'releases__php_extensions').all()
        platform_version = Version(self.kwargs['version'])

        def app_filter(app):
            for release in app.releases.all():
                if platform_version in Spec(release.platform_version_spec):
                    return True
            return False

        working_apps = list(filter(app_filter, apps))
        serializer = self.get_serializer(working_apps, many=True)
        return Response(serializer.data)


class AppReleases(DestroyAPIView):
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

            # download the latest release and create or update the models
            container = Container()
            provider = container.resolve(AppReleaseProvider)
            info = provider.get_release_info(url)
            app_id = info['app']['id']

            if serializer.validated_data['nightly']:
                info['app']['release']['version'] += '-nightly'
            version = info['app']['release']['version']

            if 'checksum' in serializer.validated_data:
                info['app']['release']['checksum'] = \
                    serializer.validated_data['checksum']
            info['app']['release']['download'] = url
            status = self._check_permission(request, app_id, version)

            importer = container.resolve(ReleaseImporter)
            importer.import_release(info)
        return Response(status=status)

    def _check_permission(self, request, app_id, version):
        # if an app does not exist, the request should create it with its
        # owner set to the currently logged in user
        try:
            app = App.objects.get(pk=app_id)
        except App.DoesNotExist:
            app = App.objects.create(pk=app_id, owner=request.user)

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

        return status

    def get_object(self):
        release = AppRelease.objects.filter(version=self.kwargs['version'],
                                            app__id=self.kwargs['app'])
        release = get_object_or_404(release)
        self.check_object_permissions(self.request, release)
        return release
