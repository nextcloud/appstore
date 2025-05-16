"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from rest_framework.throttling import ScopedRateThrottle


class PostThrottle(ScopedRateThrottle):
    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        else:
            return True
