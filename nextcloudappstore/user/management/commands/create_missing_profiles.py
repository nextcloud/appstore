from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from nextcloudappstore.user.models import UserProfile


class Command(BaseCommand):
    help = "Create missing UserProfile instances for existing users"

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            UserProfile.objects.create(user=user, subscribe_to_news=False)
            self.stdout.write(f"Created profile for user: {user.username}")

        self.stdout.write("Finished creating missing profiles.")
