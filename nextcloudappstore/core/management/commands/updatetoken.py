from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = ('Updates the API token for a user')

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--token', required=False,
                            help='If given the token is set to that value, '
                                 'otherwise a secure random value will be '
                                 'used')

    def handle(self, *args, **options):
        username = options['username']
        token = self._recreate_token(username, options.get('token', None))
        msg = 'Successfully set token %s for user %s' % (token.key, username)
        self.stdout.write(self.style.SUCCESS(msg))

    def _recreate_token(self, username: str, token: str = None) -> Token:
        user = get_user_model().objects.get(username=username)
        Token.objects.filter(user=user).delete()
        if token:
            return Token.objects.create(key=token, user=user)
        else:
            return Token.objects.create(user=user)
