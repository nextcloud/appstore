"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.core.management import BaseCommand

from nextcloudappstore.user.facades import update_token


class Command(BaseCommand):
    help = "Updates the API token for a user"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument(
            "--token",
            required=False,
            help="If given the token is set to that value, otherwise a secure random value will be used",
        )

    def handle(self, *args, **options):
        username = options["username"]
        token = update_token(username, options.get("token", None))
        msg = f"Successfully set token {token.key} for user {username}"
        self.stdout.write(self.style.SUCCESS(msg))
