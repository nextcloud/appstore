from django.http import Http404
from django.shortcuts import render, get_object_or_404

from nextcloudappstore.core.models import App, Category


def transform_version(version: str) -> str:
    if version.startswith('9x0'):
        return '9.0.0'
    elif version.startswith('9x1'):
        return '10.0.0'
    else:
        return '11.0.0'


def categories(request):
    return render(request, 'api/v0/categories.xml', {
        'categories': Category.objects.all()
    }, content_type='application/xml')


def in_category(app, category):
    categories = app.categories.all()
    for cat in categories:
        if cat.ocsid == category:
            return True
    return False


def apps(request):
    version = transform_version(request.GET.get('version'))
    category = request.GET.get('categories', None)
    compatible_apps = App.objects.get_compatible(version)
    apps = filter(lambda a: a.ocsid is not None, compatible_apps)
    if category is not None:
        apps = filter(lambda app: in_category(app, category), apps)
    return render(request, 'api/v0/apps.xml', {
        'apps': list(apps),
        'request': request,
        'version': version
    }, content_type='application/xml')


def app(request, id):
    version = transform_version(request.GET.get('version'))
    app = get_object_or_404(App, ocsid=id)
    return render(request, 'api/v0/app.xml', {
        'app': app,
        'request': request,
        'version': version
    }, content_type='application/xml')


def download(request, id):
    version = transform_version(request.GET.get('version'))
    app = get_object_or_404(App, ocsid=id)
    releases = app.compatible_releases(version)
    if len(releases) == 0:
        raise Http404('No release downloads found')
    return render(request, 'api/v0/download.xml', {
        'download': releases[0].download
    }, content_type='application/xml')
