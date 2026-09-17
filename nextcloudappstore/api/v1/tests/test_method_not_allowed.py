"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.urls import reverse

from nextcloudappstore.api.v1.tests.api import ApiTest
from nextcloudappstore.api.v1.urls import urlpatterns
from nextcloudappstore.core.models import App

# Sample kwargs per URL name, for the patterns that take any. Anything added to urls.py without an
# entry here fails the sweep below rather than being silently skipped.
URL_KWARGS = {
    "app": {"version": "9.1.0"},
    "app-download-stats": {"pk": "news"},
    "app-delete": {"pk": "news"},
    "app-release-delete": {"app": "news", "version": "1.0.0"},
}


class MethodNotAllowedTest(ApiTest):
    def test_get_on_the_delete_route_is_405_not_500(self):
        App.objects.create(id="news", owner=self.user)
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})

        response = self.api_client.get(url)

        self.assertEqual(405, response.status_code)

    def test_the_405_advertises_only_the_methods_that_work(self):
        App.objects.create(id="news", owner=self.user)
        url = reverse("api:v1:app-delete", kwargs={"pk": "news"})

        allow = self.api_client.get(url).headers["Allow"]

        self.assertIn("DELETE", allow)
        self.assertNotIn("GET", allow)

    def test_the_platform_listing_still_answers_get(self):
        """Guards the other half of the split: the listing must not move with the handler."""
        url = reverse("api:v1:app", kwargs={"version": "9.1.0"})

        self.assertEqual(200, self.api_client.get(url).status_code)

    def test_no_route_answers_an_unsupported_method_with_a_server_error(self):
        """The sweep that would have caught this class of bug.

        A view bound to two routes with different URL kwargs only breaks when a method it never
        meant to serve is dispatched to a handler expecting the other route's kwargs. No
        per-endpoint test looks for that, because nobody writes a test for a capability they did
        not know the route had.
        """
        App.objects.create(id="news", owner=self.user)
        failures = []

        for pattern in urlpatterns:
            name = pattern.name
            url = reverse(f"api:v1:{name}", kwargs=URL_KWARGS.get(name, {}))
            for method in ("get", "post", "put", "patch", "delete"):
                status = getattr(self.api_client, method)(url).status_code
                if status >= 500:
                    failures.append(f"{method.upper()} {url} ({name}) returned {status}")

        self.assertEqual([], failures)
