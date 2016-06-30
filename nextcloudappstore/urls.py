from django.conf.urls import url, include
from django.contrib import admin

from nextcloudappstore.core.views import AppListView, AppDetailView

urlpatterns = [
    url(r'^$', AppListView.as_view(), {'id': None}, name='home'),
    url(r'^', include('allauth.urls')),
    url(r'^categories/(?P<id>[\w]*)$', AppListView.as_view(),
        name='app-list'),
    url(r'^app/(?P<id>[\w]+)$', AppDetailView.as_view(), name='app-detail'),
    url(r'^api/', include('nextcloudappstore.core.api.urls',
                          namespace='api')),
    url(r'^admin/', admin.site.urls),
]
