from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from nextcloudappstore.core.facades import read_relative_file, \
    write_relative_file
from nextcloudappstore.core.models import Category


class TranslationsCommandTest(TestCase):
    def setUp(self):
        self.trans_path = '../../../templates/translation/db_translations.txt'
        self.translations = self.read_translations()

    def test_export_translations(self):
        call_command('createdbtranslations', stdout=StringIO())

        self.assertEqual('', self.read_translations())
        call_command('loaddata', 'categories.json', stdout=StringIO())
        call_command('createdbtranslations', stdout=StringIO())

        self.assertEqual(self.translations, self.read_translations())

    def test_import_translations(self):
        call_command('loaddata', 'categories.json', stdout=StringIO())
        call_command('createdbtranslations', stdout=StringIO())
        call_command('importdbtranslations', stdout=StringIO())
        category = Category.objects.get(id='organization')
        category.set_current_language('de')

        self.assertEqual('Organisation', category.name)

    def read_translations(self):
        return read_relative_file(__file__, self.trans_path).strip()

    def tearDown(self):
        write_relative_file(__file__, self.trans_path, self.translations)
