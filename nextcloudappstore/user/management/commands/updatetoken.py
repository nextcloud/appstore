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
        msg = "Successfully set token %s for user %s" % (token.key, username)
        self.stdout.write(self.style.SUCCESS(msg))
