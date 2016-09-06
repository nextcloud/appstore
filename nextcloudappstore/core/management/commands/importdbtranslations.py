from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import activate, deactivate, ugettext

from nextcloudappstore.core.models import Category


class Command(BaseCommand):
    help = 'Imports all database translations from their respective .po files'

    def handle(self, *args, **options):
        # The following code is intended to be very confusing to read
        for code, trans in settings.LANGUAGES:
            activate(code)
            self._import_category_translations(code)
            deactivate()

        msg = 'Imported db translations'
        self.stdout.write(self.style.SUCCESS(msg))

    def _import_category_translations(self, code):
        for category in Category.objects.all():
            update_category = False
            category.set_current_language('en')
            name = ugettext(category.name)
            description = ugettext(category.description)
            category.set_current_language(code)

            if name != '' and category.name != name:
                msg = ('Update Category.name for %s: "%s" -> "%s"'
                       % (code, category.name, name))
                self._print(msg)
                category.name = name
                update_category = True
            if description != '' and category.description != description:
                msg = ('Update Category.description for %s: "%s" -> "%s"'
                       % (code, category.description, description))
                self._print(msg)
                category.description = description
                update_category = True

            if update_category:
                category.save()

    def _print(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))
