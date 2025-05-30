"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class ApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")
        self.api_client = APIClient()

    def _login(self, user="test", password="test"):
        credentials = f"{user}:{password}"
        base64_credentials = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode(HTTP_HEADER_ENCODING)
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Basic {base64_credentials}")

    def _login_token(self, user="test"):
        token = "Token " + Token.objects.get(user__username=user).key
        self.api_client.credentials(HTTP_AUTHORIZATION=token)

    def tearDown(self):
        self.user.delete()
