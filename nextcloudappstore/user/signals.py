from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from rest_framework.authtoken.models import Token

from nextcloudappstore.user.facades import update_token


@receiver(post_save, sender=settings.AUTH_USER_MODEL,
          dispatch_uid="create_token")
def post_save_create_token(sender, **kwargs):
    if kwargs['created']:
        t = Token.objects.create(user=kwargs['instance'])
        t.save()


@receiver(pre_save, sender=get_user_model())
def password_changed_signal(sender, instance, **kwargs):
    """
    Regenerate token on password change
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    mail_subect = _('Nextcloud Appstore password changed')
    mail_message = _('Your Appstore password has changed. '
                     'Contact support if this wasn\'t you.')

    try:
        user = get_user_model().objects.get(pk=instance.pk)
        if user.password != instance.password:
            update_token(user.username)
            send_mail(
                    mail_subect,
                    mail_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    False)
    except User.DoesNotExist:
        pass
