from django.conf.urls import url, include
from django.contrib import admin

from nextcloudappstore.core.views import CategoryAppListView, AppDetailView, \
    app_description

urlpatterns = [
    url(r'^$', CategoryAppListView.as_view(), {'id': None}, name='home'),
    url(r'^', include('allauth.urls')),
    url(r'^categories/(?P<id>[\w]*)/?$', CategoryAppListView.as_view(),
        name='category-app-list'),
    url(r'^app/(?P<id>[\w_]+)/?$', AppDetailView.as_view(), name='app-detail'),
    url(r'^app/(?P<id>[\w_]+)/description/?$', app_description,
        name='app-description'),
    url(r'^api/', include('nextcloudappstore.core.api.urls',
                          namespace='api')),
    url(r'^admin/', admin.site.urls),
]
