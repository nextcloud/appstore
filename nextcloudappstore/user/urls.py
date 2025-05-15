"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.urls import path, re_path

from nextcloudappstore.scaffolding.views import IntegrationScaffoldingView
from nextcloudappstore.user.views import (
    AccountView,
    APITokenView,
    AppealCommentsView,
    ChangeLanguageView,
    DeleteAccountView,
    EnterpriseAppsView,
    IntegrationsView,
    PasswordView,
    TransferAppsView,
)

app_name = "user"

urlpatterns = [
    path("", AccountView.as_view(), name="account"),
    re_path(r"^integrations/?$", IntegrationsView.as_view(), name="account-integrations"),
    re_path(r"^integrations/(?P<pk>[a-z0-9_]+)/?$", IntegrationScaffoldingView.as_view(), name="account-integration"),
    re_path(
        r"^integrations/(?P<pk>[a-z0-9_]+)/moderate/?$",
        IntegrationScaffoldingView.as_view(),
        name="account-integration-moderate",
    ),
    re_path(r"^transfer-apps/?$", TransferAppsView.as_view(), name="account-transfer-apps"),
    re_path(r"^transfer-apps/(?P<pk>[a-z0-9_]+)/?$", TransferAppsView.as_view(), name="account-transfer-app"),
    re_path(r"^orphan-apps/(?P<pk>[a-z0-9_]+)/?$", TransferAppsView.as_view(), name="account-orphan-app"),
    re_path(r"^enterprise-apps/?$", EnterpriseAppsView.as_view(), name="account-enterprise-apps"),
    re_path(r"^enterprise-apps/(?P<pk>[a-z0-9_]+)/?$", EnterpriseAppsView.as_view(), name="account-enterprise-app"),
    re_path(r"^password/?$", PasswordView.as_view(), name="account-password"),
    re_path(r"^token/?$", APITokenView.as_view(), name="account-api-token"),
    re_path(r"^delete/?$", DeleteAccountView.as_view(), name="account-deletion"),
    re_path(r"^change-language/?$", ChangeLanguageView.as_view(), name="account-change-language"),
    re_path(r"^appeal-comments/?$", AppealCommentsView.as_view(), name="appeal-comments"),
]
