"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import re
from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.core import ratelimit
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from email_validator import validate_email as _real_validate_email
from rest_framework.authtoken.models import Token

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


class PasswordChangedSignalTest(TestCase):
    def setUp(self):
        self.user = create_user(username="pwuser", password=PASSWORD, email=PRIMARY_EMAIL)

    def test_password_change_persists_when_email_succeeds(self):
        old_hash = self.user.password
        self.user.set_password("New-Sup3rS3cret!")
        self.user.save()

        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertNotEqual(old_hash, refreshed.password)

    def test_password_change_not_persisted_when_email_fails(self):
        old_hash = self.user.password
        self.user.set_password("New-Sup3rS3cret!")

        with patch("nextcloudappstore.user.signals.send_mail", side_effect=Exception("SMTP down")):
            with self.assertRaises(ValidationError):
                self.user.save()

        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(old_hash, refreshed.password)

    def test_token_not_regenerated_when_email_fails(self):
        old_token = Token.objects.get(user=self.user).key
        self.user.set_password("New-Sup3rS3cret!")

        with patch("nextcloudappstore.user.signals.send_mail", side_effect=Exception("SMTP down")):
            with self.assertRaises(ValidationError):
                self.user.save()

        self.assertEqual(old_token, Token.objects.get(user=self.user).key)

    def test_no_email_sent_when_password_unchanged(self):
        with patch("nextcloudappstore.user.signals.send_mail") as mock_send_mail:
            self.user.first_name = "Changed"
            self.user.save()

        mock_send_mail.assert_not_called()


class PasswordChangeViewFriendlyErrorTest(TestCase):
    """The logged-in /account/password/ form must show a warning, not crash,
    when password_changed_signal aborts the save."""

    def setUp(self):
        self.user = create_user(username="pwchangeuser", password=PASSWORD, email=PRIMARY_EMAIL)
        self.client.login(username="pwchangeuser", password=PASSWORD)
        self.url = reverse("user:account-password")

    def _post(self, new_password="New-Sup3rS3cret!"):  # nosec
        return self.client.post(
            self.url,
            {
                "oldpassword": PASSWORD,
                "password1": new_password,
                "password2": new_password,
            },
        )

    def test_change_persists_when_email_succeeds(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)
        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(refreshed.check_password("New-Sup3rS3cret!"))

    def test_change_shows_warning_instead_of_crashing_when_email_fails(self):
        with patch("nextcloudappstore.user.signals.send_mail", side_effect=Exception("SMTP down")):
            response = self._post()

        self.assertEqual(response.status_code, 200)
        shown_messages = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("not changed" in m for m in shown_messages))
        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(refreshed.check_password(PASSWORD))


class PasswordResetFromKeyViewFriendlyErrorTest(TestCase):
    """The forgot-password flow must show a warning, not crash, when
    password_changed_signal aborts the save."""

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
        self.user = create_user(username="resetuser", password=PASSWORD, email=PRIMARY_EMAIL)

    def tearDown(self):
        # Each test consumes the "reset_password" rate-limit budget for this
        # IP; clear it so it doesn't bleed into unrelated tests that run
        # right after (e.g. the reset-password e2e test).
        cache.clear()

    def _get_set_password_url(self):
        self.client.post(reverse("account_reset_password"), {"email": PRIMARY_EMAIL})
        body = mail.outbox[-1].body
        match = re.search(r"https?://[^\s]+(/password/reset/key/\S+?)/?(?:\s|$)", body)
        response = self.client.get(match.group(1) + "/", follow=True)
        self.assertEqual(response.status_code, 200)
        return response.redirect_chain[-1][0]

    def test_reset_persists_when_email_succeeds(self):
        url = self._get_set_password_url()
        response = self.client.post(url, {"password1": "New-Sup3rS3cret!", "password2": "New-Sup3rS3cret!"})
        self.assertEqual(response.status_code, 302)
        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(refreshed.check_password("New-Sup3rS3cret!"))

    def test_reset_shows_warning_instead_of_crashing_when_email_fails(self):
        url = self._get_set_password_url()
        with patch("nextcloudappstore.user.signals.send_mail", side_effect=Exception("SMTP down")):
            response = self.client.post(url, {"password1": "New-Sup3rS3cret!", "password2": "New-Sup3rS3cret!"})

        self.assertEqual(response.status_code, 200)
        shown_messages = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("not changed" in m for m in shown_messages))
        refreshed = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(refreshed.check_password(PASSWORD))
