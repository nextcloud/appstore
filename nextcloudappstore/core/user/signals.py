from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="create_token")
def post_save_create_token(sender, **kwargs):
    if kwargs['created']:
        t = Token.objects.create(user=kwargs['instance'])
        t.save()
