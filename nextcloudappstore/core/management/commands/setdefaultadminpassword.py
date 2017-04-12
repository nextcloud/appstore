from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = ('Sets the password "admin" for the user "admin". Only use this '
            'in development!')

    def handle(self, *args, **options):
        user = get_user_model().objects.get(username='admin')
        user.set_password('admin')
        user.save()
        msg = 'Successfully set password %s for user %s' % ('admin', 'admin')
        self.stdout.write(self.style.SUCCESS(msg))
