from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = ('Activates an account by verifying the given email and user')

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        user = get_user_model().objects.get(username=username)
        address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=email,
        )
        address.verified = True
        address.primary = True
        address.save()
        msg = 'Successfully verified email %s for user %s' % (email, username)
        self.stdout.write(self.style.SUCCESS(msg))
