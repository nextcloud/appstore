"""
SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.utils.translation import gettext_lazy as _
from email_validator import EmailNotValidError, validate_email


class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        try:
            validate_email(email, check_deliverability=True, timeout=3)
        except EmailNotValidError:
            raise forms.ValidationError(_("Provided email address is not valid."))
        return email
