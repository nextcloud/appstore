from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from nextcloudappstore.user.facades import create_user


class Command(BaseCommand):
    help = (
        "Allows you to create a user by providing a login name and password. "
        "Do "
        "not use this in production since login name and password will be "
        "saved "
        "in your shell's history!"
    )

    def add_arguments(self, parser):
        social_meta = get_user_model()._meta
        parser.add_argument("--username", required=True, help=social_meta.get_field("username").help_text)
        parser.add_argument("--password", required=True, help=social_meta.get_field("password").help_text)
        parser.add_argument("--email", required=True, help=social_meta.get_field("email").help_text)

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]
        user = create_user(username, password, email)
        msg = "Created user %s with password %s and email %s" % (user, password, email)
        self.stdout.write(self.style.SUCCESS(msg))
