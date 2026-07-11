"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.core import ratelimit
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from email_validator import validate_email as _real_validate_email

from nextcloudappstore.user.facades import create_user

PASSWORD = "Sup3rS3cret!"
PRIMARY_EMAIL = "user@example.com"


def _validate_email_no_dns(email, **kwargs):
    # Run the real format/empty checks but skip the DNS-deliverability lookup
    # so tests don't depend on external resolvers.
    kwargs["check_deliverability"] = False
    return _real_validate_email(email, **kwargs)


@override_settings(
    ACCOUNT_RATE_LIMITS={
        "reset_password": "1/m/ip",
        "login_failed": "10/h/ip",
        "manage_email": "3/h/user",
    },
)
class AccountEmailChangeRateLimitTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._validate_patcher = patch(
            "nextcloudappstore.user.adapters.validate_email",
            side_effect=_validate_email_no_dns,
        )
        cls._validate_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls._validate_patcher.stop()
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.user = create_user(username="testuser", password=PASSWORD, email=PRIMARY_EMAIL)
        self.client.login(username="testuser", password=PASSWORD)
        self.url = reverse("user:account")

    def _post(self, **overrides):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": PRIMARY_EMAIL,
            "subscribe_to_news": False,
            "passwd": PASSWORD,
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_no_email_change_does_not_consume_budget(self):
        for i in range(10):
            response = self._post(first_name=f"Name{i}")
            self.assertEqual(response.status_code, 302, f"iteration {i}")

    def test_first_email_change_within_limit_succeeds(self):
        response = self._post(email="new1@nextcloud.com")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EmailAddress.objects.filter(user=self.user, email="new1@nextcloud.com", verified=False).exists()
        )

    def test_email_change_blocked_after_limit_exceeded(self):
        for i in range(1, 4):
            response = self._post(email=f"new{i}@nextcloud.com")
            self.assertEqual(response.status_code, 302, f"iteration {i}")

        response = self._post(email="new4@nextcloud.com")
        self.assertEqual(response.status_code, 429)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(EmailAddress.objects.filter(email="new4@nextcloud.com").exists())

    def test_user_email_unchanged_when_rate_limited(self):
        for i in range(1, 4):
            self._post(email=f"new{i}@nextcloud.com")
        before = get_user_model().objects.get(pk=self.user.pk).email

        self._post(email="new4@nextcloud.com")
        after = get_user_model().objects.get(pk=self.user.pk).email

        self.assertEqual(after, before)
        self.assertNotEqual(after, "new4@nextcloud.com")

    def test_name_changes_persist_when_email_rate_limited(self):
        for i in range(1, 4):
            self._post(email=f"new{i}@nextcloud.com")

        self._post(
            email="new4@nextcloud.com",
            first_name="NewFirst",
            last_name="NewLast",
        )

        updated = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(updated.first_name, "NewFirst")
        self.assertEqual(updated.last_name, "NewLast")

    def test_rate_limit_independent_from_reset_password(self):
        for i in range(1, 4):
            self._post(email=f"new{i}@nextcloud.com")

        request = RequestFactory().post(self.url)
        self.assertTrue(ratelimit.consume(request, action="reset_password"))

    def test_invalid_form_does_not_consume_budget(self):
        for i in range(5):
            response = self._post(
                email=f"newX{i}@nextcloud.com",
                passwd="wrong-password",  # nosec
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)

        for i in range(1, 4):
            response = self._post(email=f"valid{i}@nextcloud.com")
            self.assertEqual(response.status_code, 302, f"iteration {i}")

    def test_same_email_submission_does_not_consume_budget(self):
        for _ in range(10):
            response = self._post()
            self.assertEqual(response.status_code, 302)

        for i in range(1, 4):
            response = self._post(email=f"changed{i}@nextcloud.com")
            self.assertEqual(response.status_code, 302, f"iteration {i}")

    def test_case_only_email_change_does_not_consume_budget(self):
        # allauth stores EmailAddress.email lowercased and add_email() lowercases
        # on the way in, so submitting the same address in different case is a
        # silent no-op. The rate-limit budget must reflect that.
        for _ in range(10):
            response = self._post(email=PRIMARY_EMAIL.upper())
            self.assertEqual(response.status_code, 302)
        for i in range(1, 4):
            response = self._post(email=f"changed{i}@nextcloud.com")
            self.assertEqual(response.status_code, 302, f"iteration {i}")

    def test_odoo_called_with_actual_email_when_rate_limited(self):
        for i in range(1, 4):
            self._post(email=f"new{i}@nextcloud.com")

        with patch("nextcloudappstore.user.models.subscribe_user_to_news") as mock_sub:
            # Flipping subscribe_to_news triggers the pre_save handler in
            # signals.py; it must not be passed the rejected new email.
            self._post(email="new4@nextcloud.com", subscribe_to_news=True)

        if mock_sub.called:
            called_with_email = mock_sub.call_args[0][0]
            self.assertNotEqual(called_with_email, "new4@nextcloud.com")

    def test_empty_email_rejected_by_form(self):
        response = self._post(email="")
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(EmailAddress.objects.filter(email="").exists())

    def test_malformed_email_rejected_by_form(self):
        response = self._post(email="not-an-email")
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)

    def test_budget_shared_with_allauth_email_view(self):
        for i in range(1, 4):
            r = self._post(email=f"viaaccount{i}@nextcloud.com")
            self.assertEqual(r.status_code, 302, f"iteration {i}")

        email_url = reverse("account_email")
        r = self.client.post(email_url, {"email": "viaemail@nextcloud.com", "action_add": ""})
        self.assertEqual(r.status_code, 429)


@override_settings(
    ACCOUNT_RATE_LIMITS={
        "reset_password": "1/m/ip",
        "login_failed": "10/h/ip",
        "manage_email": "3/h/user",
    },
)
class GitHubOnlyAccountEditTest(TestCase):
    """A user who signed up via GitHub has no usable password, so the
    account edit form must not demand one to confirm critical changes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._validate_patcher = patch(
            "nextcloudappstore.user.adapters.validate_email",
            side_effect=_validate_email_no_dns,
        )
        cls._validate_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls._validate_patcher.stop()
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.user = create_user(username="githubuser", password="unused", email=PRIMARY_EMAIL)  # nosec
        self.user.set_unusable_password()
        self.user.save()
        SocialAccount.objects.create(user=self.user, provider="github", uid="12345")
        self.client.force_login(self.user)
        self.url = reverse("user:account")

    def test_can_change_name_without_password(self):
        response = self.client.post(
            self.url,
            {
                "first_name": "New",
                "last_name": "Name",
                "email": PRIMARY_EMAIL,
                "subscribe_to_news": False,
                "passwd": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        updated = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(updated.first_name, "New")
        self.assertEqual(updated.last_name, "Name")

    def test_can_change_email_without_password(self):
        response = self.client.post(
            self.url,
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "newgithub@nextcloud.com",
                "subscribe_to_news": False,
                "passwd": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EmailAddress.objects.filter(user=self.user, email="newgithub@nextcloud.com", verified=False).exists()
        )
