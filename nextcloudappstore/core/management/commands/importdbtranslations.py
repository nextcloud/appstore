from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import activate, deactivate, ugettext

from nextcloudappstore.core.models import Category


class Command(BaseCommand):
    help = 'Imports all database translations from their respective .po files'

    def handle(self, *args, **options):
        translated_langs = [lang[0] for lang in settings.LANGUAGES if
                            lang[0] != 'en']
        for code in translated_langs:
            activate(code)
            self._import_category_translations(code)
            deactivate()

        msg = 'Imported db translations'
        self.stdout.write(self.style.SUCCESS(msg))

    def _import_category_translations(self, code):
        # The following code is intended to be very confusing to read
        for category in Category.objects.all():
            category.set_current_language('en')
            name_en = category.name
            description_en = category.description
            name_trans = ugettext(category.name)
            description_trans = ugettext(category.description)
            category.set_current_language(code)

            if self._has_translations(category, name_trans, description_trans):
                self._update_trans(category, 'name', code, name_en, name_trans)
                self._update_trans(category, 'description', code,
                                   description_en, description_trans)
                category.save()

    def _has_translations(self, category, name, description):
        """
        There are no new translations if:
         * the translations are the same as in the database
         * the translations are empty
        """
        return not (
            (name.strip() == '' and description.strip() == '') or
            (category.name == name and category.description == description)
        )

    def _update_trans(self, obj, attr, code, en, trans):
        if getattr(obj, attr) != trans:
            msg = ('Update Category.%s for %s: "%s" -> "%s"'
                   % (code, attr, getattr(obj, attr), trans))
            self._print(msg)
            setattr(obj, attr, trans)
        else:
            setattr(obj, attr, en)

    def _print(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))
