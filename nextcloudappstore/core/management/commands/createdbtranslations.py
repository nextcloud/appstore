from os.path import join

from django.conf import settings
from django.core.management import BaseCommand

from nextcloudappstore.core.facades import flatmap
from nextcloudappstore.core.models import Category


def escape_tpl_string(string):
    return string.replace('\\', '\\\\').replace('"', '\\"')


class Command(BaseCommand):
    translation_file = ('nextcloudappstore/core/templates/translation/'
                        'db_translations.txt')
    help = (
        'Goes through all translated database models (hardcoded) and creates '
        'translations in %s' % translation_file)
    translated_fields = (
        (Category, ('name', 'description')),
    )
    source_lang = 'en'

    def handle(self, *args, **options):
        target_file = join(settings.BASE_DIR, self.translation_file)
        translations = flatmap(lambda x: self._create_translations(x[0], x[1]),
                               self.translated_fields)
        content = '\n'.join(translations)
        with open(target_file, 'w') as f:
            f.write(content)

        msg = 'Exported translations to %s' % target_file
        self.stdout.write(self.style.SUCCESS(msg))

    def _create_translations(self, model, fields):
        objs = model.objects.language(self.source_lang).all()
        strings = flatmap(lambda o: [getattr(o, f) for f in fields], objs)
        strings = map(escape_tpl_string, strings)
        return list(map(lambda s: '{%% trans "%s" %%}' % s, strings))
