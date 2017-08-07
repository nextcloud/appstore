from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


def create_user(username: str, password: str, email: str, verify: bool = True):
    user, created = get_user_model().objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.email = email
        user.save()
    if verify:
        verify_email(username, email)
    return user


def verify_email(username, email):
    user = get_user_model().objects.get(username=username)
    address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
    )
    address.verified = True
    address.primary = True
    address.save()
    return address


def update_token(username: str, token: str = None) -> Token:
    user = get_user_model().objects.get(username=username)
    Token.objects.filter(user=user).delete()
    if token:
        return Token.objects.create(key=token, user=user)
    else:
        return Token.objects.create(user=user)


def delete_user(username):
    get_user_model().objects.get(username=username).delete()
