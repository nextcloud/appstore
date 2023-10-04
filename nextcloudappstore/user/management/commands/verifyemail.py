from django.core.management import BaseCommand

from nextcloudappstore.user.facades import verify_email


class Command(BaseCommand):
    help = "Activates an account by verifying the given email and user"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        verify_email(username, email)
        msg = f"Successfully verified email {email} for user {username}"
        self.stdout.write(self.style.SUCCESS(msg))
