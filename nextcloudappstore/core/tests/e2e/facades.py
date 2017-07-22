from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model


def create_user(username, password, email):
    user = get_user_model().objects.create_user(
        username=username,
        password=password,
        email=email,
    )
    address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
    )
    address.verified = True
    address.primary = True
    address.save()
    return user


def delete_user(username):
    get_user_model().objects.get(username=username).delete()
