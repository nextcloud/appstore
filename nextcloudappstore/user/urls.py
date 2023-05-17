from django.conf.urls import url

from nextcloudappstore.scaffolding.views import IntegrationScaffoldingView
from nextcloudappstore.user.views import (
    AccountView,
    APITokenView,
    ChangeLanguageView,
    DeleteAccountView,
    IntegrationsView,
    PasswordView,
    TransferAppsView,
)

app_name = "user"

urlpatterns = [
    url(r"^$", AccountView.as_view(), name="account"),
    url(r"^integrations/?$", IntegrationsView.as_view(), name="account-integrations"),
    url(r"^integrations/(?P<pk>[a-z0-9_]+)/?$", IntegrationScaffoldingView.as_view(), name="account-integration"),
    url(
        r"^integrations/(?P<pk>[a-z0-9_]+)/moderate/?$",
        IntegrationScaffoldingView.as_view(),
        name="account-integration-moderate",
    ),
    url(r"^transfer-apps/?$", TransferAppsView.as_view(), name="account-transfer-apps"),
    url(r"^transfer-apps/(?P<pk>[a-z0-9_]+)/?$", TransferAppsView.as_view(), name="account-transfer-app"),
    url(r"^password/?$", PasswordView.as_view(), name="account-password"),
    url(r"^token/?$", APITokenView.as_view(), name="account-api-token"),
    url(r"^delete/?$", DeleteAccountView.as_view(), name="account-deletion"),
    url(r"^change-language/?$", ChangeLanguageView.as_view(), name="account-change-language"),
]
