from django.conf.urls import url

from nextcloudappstore.core.api.v0.views import categories, apps, app, download

urlpatterns = [
    url(r'^content/categories/?$', categories, name='categories'),
    url(r'^content/data/?$', apps, name='apps'),
    url(r'^content/data/(?P<id>[\w]*)/?$', app, name='app'),
    url(r'^content/download/(?P<id>[\w]*)/1/?$', download,
        name='download'),
]
