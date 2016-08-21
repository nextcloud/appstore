from allauth.account.views import signup
from allauth.socialaccount.views import signup as social_signup
from csp.decorators import csp_exempt
from django.conf.urls import url, include
from django.contrib import admin
from nextcloudappstore.core.user.views import \
    PasswordView, AccountView, APITokenView
from nextcloudappstore.core.views import CategoryAppListView, AppDetailView, \
    app_description, AppReleasesView, AppUploadView, LegalNoticeView

urlpatterns = [
    url(r'^$', CategoryAppListView.as_view(), {'id': None}, name='home'),
    url(r"^signup/$", csp_exempt(signup), name="account_signup"),
    url(r"^social/signup/$", csp_exempt(social_signup),
        name="socialaccount_signup"),
    url(r'^', include('allauth.urls')),
    url(r'^account/?$', AccountView.as_view(), name='account'),
    url(r'^account/password/?$', PasswordView.as_view(),
        name='account-password'),
    url(r'^account/token/?$', APITokenView.as_view(),
        name='account-api-token'),
    url(r'^legal/?$', LegalNoticeView.as_view(), name='legal-notice'),
    url(r'^categories/(?P<id>[\w]*)/?$', CategoryAppListView.as_view(),
        name='category-app-list'),
    url(r'^app/upload/?$', AppUploadView.as_view(), name='app-upload'),
    url(r'^app/(?P<id>[\w_]+)/?$', AppDetailView.as_view(), name='app-detail'),
    url(r'^app/(?P<id>[\w_]+)/releases/?$', AppReleasesView.as_view(),
        name='app-releases'),
    url(r'^app/(?P<id>[\w_]+)/description/?$', app_description,
        name='app-description'),
    url(r'^api/', include('nextcloudappstore.core.api.urls',
                          namespace='api')),
    url(r'^admin/', admin.site.urls),
]
