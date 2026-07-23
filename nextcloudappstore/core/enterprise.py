"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import logging

import requests
from django.conf import settings
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

VALIDATION_TIMEOUT = 10  # seconds


def is_enterprise_feature_enabled() -> bool:
    return bool(
        getattr(settings, "ENABLE_ENTERPRISE_ONLY_APPS", False)
        and getattr(settings, "ENTERPRISE_KEY_VALIDATION_ENDPOINT", "")
        and getattr(settings, "ENTERPRISE_KEY_VALIDATION_API_KEY", "")
    )


def validate_subscription_key(subscription_key: str) -> bool:
    if not is_enterprise_feature_enabled() or not subscription_key:
        return False
    try:
        response = requests.post(
            settings.ENTERPRISE_KEY_VALIDATION_ENDPOINT,
            json={"subscriptionKey": subscription_key},
            headers={"Authorization": f"Bearer {settings.ENTERPRISE_KEY_VALIDATION_API_KEY}"},
            timeout=VALIDATION_TIMEOUT,
        )
        response.raise_for_status()
        return bool(response.json().get("valid", False))
    except (requests.RequestException, ValueError):
        logger.warning("Failed to validate enterprise subscription key", exc_info=True)
        return False


def enterprise_enabled(request) -> bool:
    if not hasattr(request, "_enterprise_enabled"):
        subscription_key = request.GET.get("subscription_key", "")
        request._enterprise_enabled = validate_subscription_key(subscription_key)
    return request._enterprise_enabled


def filter_enterprise(queryset: QuerySet, request) -> QuerySet:
    """Filter out enterprise-only apps unless a valid subscription key is provided."""
    if not enterprise_enabled(request):
        queryset = queryset.filter(is_enterprise_only=False)
    return queryset
