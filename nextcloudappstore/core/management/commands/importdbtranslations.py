from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import activate, deactivate, ugettext

from nextcloudappstore.core.models import Category


class Command(BaseCommand):
    help = 'Imports all database translations from their respective .po files'

    def handle(self, *args, **options):
        categories = Category.objects.language('en').all()
        for code, trans in settings.LANGUAGES:
            activate(code)
            for category in categories:
                category.set_current_language('en')
                name = ugettext(category.name)
                description = ugettext(category.description)
                if name:
                    category.set_current_language(code)
                    category.name = name
                if description:
                    category.set_current_language(code)
                    category.name = description
                category.save()
            deactivate()

        msg = 'Imported db translations'
        self.stdout.write(self.style.SUCCESS(msg))
