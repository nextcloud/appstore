# DO NOT run this in production
# Setup code for dev environment and test setup

from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from rest_framework.authtoken.models import Token


def create_mail(user: User) -> EmailAddress:
    return EmailAddress.objects.create(
        user=user,
        email='%s@example.com' % user.username,
        verified=True,
        primary=True
    )


def create_token(user: User, token: str):
    token = Token.objects.get(user=user)
    token.key = token
    return token.save()


admin = User.objects.create_superuser(
    'admin',
    'admin@example.com',
    'admin'
)

create_mail(admin)
