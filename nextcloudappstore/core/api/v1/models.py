from django.db.models import DateTimeField, Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from nextcloudappstore.core.models import AppRelease, App


@receiver(post_delete, sender=App)
def record_app_delete(sender, **kwargs):
    AppReleaseDeleteLog.objects.create()


@receiver(post_delete, sender=AppRelease)
def record_app_release_delete(sender, **kwargs):
    AppReleaseDeleteLog.objects.create()


class AppReleaseDeleteLog(Model):
    """
    Used to keep track of app and app release deletions
    """
    last_modified = DateTimeField(auto_now=True, db_index=True)
