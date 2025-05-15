"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("v1/", include("nextcloudappstore.api.v1.urls", namespace="v1")),
]
