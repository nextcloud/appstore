from django.conf.urls import url

from nextcloudappstore.core.user.views import PasswordView, AccountView, \
    APITokenView, DeleteAccountView, ChangeLanguageView

urlpatterns = [
    url(r'^$', AccountView.as_view(), name='account'),
    url(r'^password/?$', PasswordView.as_view(), name='account-password'),
    url(r'^token/?$', APITokenView.as_view(), name='account-api-token'),
    url(r'^delete/?$', DeleteAccountView.as_view(), name='account-deletion'),
    url(r'^change-language/?$', ChangeLanguageView.as_view(),
        name='account-change-language'),
]
