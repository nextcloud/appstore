from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.translation import ugettext
from parler.models import TranslatableModel
from parler.utils.context import switch_language

from nextcloudappstore.core.models import Category


class Command(BaseCommand):
    help = "Imports all database translations from their respective .po files"
    translated_fields = ((Category, ("name", "description")),)
    source_lang = "en"

    def handle(self, *args, **options):
        language_codes = [language[0] for language in settings.LANGUAGES if language[0] != self.source_lang]
        for language_code in language_codes:
            for model, fields in self.translated_fields:
                if issubclass(model, TranslatableModel):
                    self._import_translations(model, fields, language_code)
                else:
                    raise CommandError('Model "%s" is not translatable' % model.__name__)
        self.stdout.write(self.style.SUCCESS("Imported db translations"))

    def _import_translations(self, model, fields, language_code):
        """
        Import translations for fields on a model for a language code
        :param model: the translated model
        :param fields: the attributes to translate
        :param language_code: the language code
        :return:
        """
        for obj in model.objects.all():
            with switch_language(obj, language_code):
                if obj.has_translation(language_code):
                    obj.delete_translation(language_code)
                source = [self._get_en(obj, field) for field in fields]
                translations = [ugettext(value) for value in source]
                for field, translation in zip(fields, translations):
                    setattr(obj, field, translation)
                    obj.save()

    def _get_en(self, obj, field):
        return obj.safe_translation_getter(field, language_code=self.source_lang)
