from nextcloudappstore.core.api.v1.serializers import AppSerializer
from nextcloudappstore.core.models import App
from nextcloudappstore.core.permissions import AllowedToEditApp
from rest_framework import authentication
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from semantic_version import Version
import sys


def pad_max_version(version):
    while version.count('.') < 2:
        version += '.%i' % sys.maxsize
    return version


def pad_version(version):
    while version.count('.') < 2:
        version += '.0'
    return version


def includes_release(release, version_string):
    version = Version(pad_version(version_string))
    includes_min = True
    includes_max = True
    if release.platform_min:
        min_version = pad_version(release.platform_min)
        includes_min = Version(min_version) <= version
    if release.platform_max:
        max_version = pad_max_version((release.platform_max))
        includes_max = Version(max_version) >= version
    return includes_max and includes_min


def app_has_included_release(app, version_string):
    releases = app.releases.all()
    releases = filter(lambda r: includes_release(r, version_string), releases)
    return len(list(releases)) > 0


class Apps(DestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, AllowedToEditApp)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        apps = App.objects.prefetch_related('categories', 'authors',
                                            'releases',
                                            'releases__databases',
                                            'releases__libs').all()

        def app_filter(app):
            return app_has_included_release(app, self.kwargs['version'])

        working_apps = list(filter(app_filter, apps))
        serializer = self.get_serializer(working_apps, many=True)
        return Response(serializer.data)


class AppReleases(GenericAPIView):
    pass
