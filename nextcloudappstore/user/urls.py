from django.conf.urls import url

from nextcloudappstore.user.views import PasswordView, AccountView, \
    APITokenView, DeleteAccountView, ChangeLanguageView, TransferAppsView

urlpatterns = [
    url(r'^$', AccountView.as_view(), name='account'),
    url(r'^transfer-apps/?$', TransferAppsView.as_view(),
        name='account-transfer-apps'),
    url(r'^transfer-apps/(?P<pk>[a-z0-9_]+)/?$', TransferAppsView.as_view(),
        name='account-transfer-app'),
    url(r'^password/?$', PasswordView.as_view(), name='account-password'),
    url(r'^token/?$', APITokenView.as_view(), name='account-api-token'),
    url(r'^delete/?$', DeleteAccountView.as_view(), name='account-deletion'),
    url(r'^change-language/?$', ChangeLanguageView.as_view(),
        name='account-change-language'),
]
