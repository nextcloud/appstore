"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "nextcloudappstore.api"
    verbose_name = "App Store REST API"
