from functools import reduce

from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import CommandError
from django.utils.translation import activate, deactivate, ugettext
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
        langs = [lang[0] for lang in settings.LANGUAGES if
                 lang[0] != self.source_lang]
        for code in langs:
            activate(code)
            for model, attrs in self.translated_fields:
                if issubclass(model, TranslatableModel):
                    self._import_translations(model, attrs, code, is_verbose)
                else:
                    msg = 'Model "%s" is not translatable' % model.__name__
                    raise CommandError(msg)
            deactivate()

        msg = 'Imported db translations'
        self.stdout.write(self.style.SUCCESS(msg))

    def _import_translations(self, model, attrs, code, is_verbose=False):
        """
        Import translations for fields on a model for a language code
        :param model: the translated model
        :param attrs: the attributes to translate
        :param code: the language code
        :return:
        """
        for obj in model.objects.all():
            obj.set_current_language(self.source_lang)
            attrs_src = list(map(lambda f: getattr(obj, f), attrs))
            attrs_trans = list(map(lambda f: ugettext(f), attrs_src))
            obj.set_current_language(code)

            if self._has_translations(obj, attrs, attrs_trans):
                for attr, src, trans in zip(attrs, attrs_src, attrs_trans):
                    self._update_trans(obj, attr, code, src, trans, is_verbose)
                obj.save()

    def _has_translations(self, obj, attrs, attrs_trans):
        """
        Checks if any of the attributes has a translation
        :param obj: translatable model instance
        :param attrs: model attributes to check
        :param attrs_trans: translated fields for the current attribute values
        :return: True if the model has translations for the current code
        """
        translations_present = [self._has_translation(*(obj, attr, trans))
                                for attr, trans
                                in zip(attrs, attrs_trans)]
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
