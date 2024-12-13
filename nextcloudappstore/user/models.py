from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .odoo import subscribe_user_to_news, unsubscribe_user_from_news


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    subscribe_to_news = models.BooleanField(
        default=True, help_text="User has opted in to receive Nextcloud news and updates."
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


# Signal to create a profile for each new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# Detect changes to subscribe_to_news and trigger actions
@receiver(pre_save, sender=UserProfile)
def handle_subscription_change(sender, instance, **kwargs):
    if instance.pk:  # Ensure this is an update, not a creation
        # Fetch the old value of subscribe_to_news
        old_value = UserProfile.objects.filter(pk=instance.pk).values_list("subscribe_to_news", flat=True).first()
        new_value = instance.subscribe_to_news

        if old_value != new_value:
            if new_value:
                # Logic to subscribe the user
                subscribe_user_to_news(instance.user)
            else:
                # Logic to unsubscribe the user
                unsubscribe_user_from_news(instance.user)
