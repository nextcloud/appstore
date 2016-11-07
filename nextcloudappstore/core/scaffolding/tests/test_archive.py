import tarfile

from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.scaffolding.archive import build_files, \
    build_archive


class ArchiveTest(TestCase):
    def setUp(self):
        self.args = {
            'name': 'TheApp',
            'summary': 'a summary',
            'description': 'a description',
            'author_name': 'author name',
            'author_email': 'author email',
            'author_homepage': 'author homepage',
            'platform': '11',
            'categories': ['tools'],
        }

    def test_build_files(self):
        expected = read_relative_file(__file__, 'data/info.xml').strip()
        result = build_files(self.args)
        info = result['theapp/appinfo/info.xml'].strip()
        self.assertEqual(expected, info)

    def test_no_int_version(self):
        with self.assertRaises(ValueError):
            build_files({'platform': 'test'})

    def test_no_directory(self):
        self.args['platform'] = '8'
        result = build_files(self.args)
        self.assertDictEqual({}, result)

    def test_build_archive(self):
        result = build_archive(self.args)
        expected = read_relative_file(__file__, 'data/info.xml').strip()
        with tarfile.open(fileobj=result, mode='r:gz') as f:
            member = f.getmember('theapp/appinfo/info.xml')
            with f.extractfile(member) as info:
                result = info.read().strip().decode('utf-8')
                self.assertEqual(expected, result)
