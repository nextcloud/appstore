from nextcloudappstore.core.api.v1.serializers import AppSerializer
from nextcloudappstore.core.models import App, AppRelease
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.versioning import app_has_included_release
from rest_framework import authentication
from rest_framework.generics import DestroyAPIView, get_object_or_404
from rest_framework.response import Response


class Apps(DestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        apps = App.objects.prefetch_related('translations',
                                            'categories__translations',
                                            'categories', 'authors',
                                            'releases', 'screenshots',
                                            'releases__databases',
                                            'releases__libs').all()

        def app_filter(app):
            return app_has_included_release(app, self.kwargs['version'])

        working_apps = list(filter(app_filter, apps))
        serializer = self.get_serializer(working_apps, many=True)
        return Response(serializer.data)


class AppReleases(DestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission,)

    def get_object(self):
        release = AppRelease.objects.filter(version=self.kwargs['version'],
                                            app__id=self.kwargs['app'])
        release = get_object_or_404(release)
        self.check_object_permissions(self.request, release)
        return release
