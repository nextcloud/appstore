from functools import reduce

from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import CommandError
from django.utils.translation import activate, ugettext
from parler.models import TranslatableModel

from nextcloudappstore.core.models import Category


class Command(BaseCommand):
    help = 'Imports all database translations from their respective .po files'
    translated_fields = (
        (Category, ('name', 'description')),
    )
    source_lang = 'en'

    def handle(self, *args, **options):
        is_verbose = options['verbosity'] >= 2
        language_codes = [language[0] for language in settings.LANGUAGES if
                          language[0] != self.source_lang]
        for language_code in language_codes:
            for model, fields in self.translated_fields:
                if issubclass(model, TranslatableModel):
                    self._import_translations(model, fields, language_code,
                                              is_verbose)
                else:
                    msg = 'Model "%s" is not translatable' % model.__name__
                    raise CommandError(msg)

        msg = 'Imported db translations'
        self.stdout.write(self.style.SUCCESS(msg))

    def _import_translations(self, model, fields, language_code, is_verbose):
        """
        Import translations for fields on a model for a language code
        :param model: the translated model
        :param fields: the attributes to translate
        :param language_code: the language code
        :return:
        """
        for obj in model.objects.all():
            obj.set_current_language(self.source_lang, True)
            english_values = [getattr(obj, field) for field in fields]

            activate(language_code)
            translated_values = [ugettext(value) for value in english_values]
            obj.set_current_language(language_code, True)
            if self._has_translations(obj, fields, translated_values):
                for field, english, translation in zip(fields, english_values,
                                                       translated_values):
                    self._update_trans(obj, field, language_code, english,
                                       translation, is_verbose)
                obj.save()

    def _has_translations(self, obj, fields, translations):
        """
        Checks if any of the attributes has a translation
        :param obj: translatable model instance
        :param fields: model attributes to check
        :param translations: translated fields for the current attribute values
        :return: True if the model has translations for the current code
        """
        translations_present = [self._has_translation(obj, attr, trans)
                                for attr, trans
                                in zip(fields, translations)]
        return reduce(lambda a, b: a or b, translations_present, False)

    def _has_translation(self, obj, attr, trans):
        """
        Checks if an attribute has a translation
        :param obj: translatable model instance
        :param attrs: model attributes to check
        :param trans: translated field for the current attribute value
        :return: True if the attribute has translations for the current code
        """
        return trans.strip() != '' and getattr(obj, attr) != trans

    def _update_trans(self, obj, attr, code, src, trans, is_verbose=False):
        """
        Updates a translation for an attribute on the object
        :param obj: object which has the translatable attribute
        :param attr: attribute name
        :param code: language code
        :param src: attribute value in the source language
        :param trans: attribute value in the translated language
        :return:
        """
        if getattr(obj, attr) != trans:
            if is_verbose:
                msg = ('Update %s.%s for %s: "%s" -> "%s"'
                       % (
                           obj.__class__.__name__, attr, code,
                           getattr(obj, attr),
                           trans))
                self._print(msg)
            setattr(obj, attr, trans)
        else:
            setattr(obj, attr, src)

    def _print(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))
