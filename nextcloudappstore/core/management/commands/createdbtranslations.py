from itertools import chain

from django.conf import settings
from django.core.management import BaseCommand
from os.path import join

from nextcloudappstore.core.models import Category


def flatmap(f, xs):
    return chain.from_iterable(map(f, xs))


def escape_tpl_string(string):
    return string.replace('\\', '\\\\').replace('"', '\\"')


class Command(BaseCommand):
    translation_file = ('nextcloudappstore/core/templates/translation/'
                        'db_translations.txt')
    help = (
        'Goes through all translated database models (hardcoded) and creates '
        'translations in %s' % translation_file)

    def handle(self, *args, **options):
        target_file = join(settings.BASE_DIR, self.translation_file)
        categories = Category.objects.language('en').all()
        strings = flatmap(lambda c: (c.name, c.description), categories)
        strings = map(escape_tpl_string, strings)
        wrapped_strings = map(lambda s: '{%% trans "%s" %%}' % s, strings)
        content = '\n'.join(wrapped_strings)
        with open(target_file, 'w') as f:
            f.write(content)

        msg = 'Exported translations to %s' % target_file
        self.stdout.write(self.style.SUCCESS(msg))
