from django.test import TestCase
from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.parser import \
    parse_app_metadata, GunZipAppMetadataExtractor, \
    InvalidAppPackageStructureException, \
    UnsupportedAppArchiveException, InvalidAppMetadataXmlException
from nextcloudappstore.core.facades import resolve_file_relative_path, \
    read_file_contents
from rest_framework.exceptions import APIException


class ParserTest(TestCase):
    def setUp(self):
        self.config = ReleaseConfig()
        self.maxDiff = None

    def test_parse_minimal(self):
        xml = self._get_test_xml('data/infoxmls/minimal.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        expected = {'app': {
            'id': 'news',
            'summary': {'en': 'An RSS/Atom feed reader'},
            'description': {'en': 'An RSS/Atom feed reader'},
            'name': {'en': 'News'},
            'admin_docs': None,
            'developer_docs': None,
            'user_docs': None,
            'website': None,
            'discussion': None,
            'issue_tracker': None,
            'screenshots': [],
            'categories': [{'category': {'id': 'multimedia'}}],
            'release': {
                'databases': [],
                'licenses': [{'license': {'id': 'agpl'}}],
                'min_int_size': 32,
                'php_extensions': [],
                'php_max_version': '*',
                'php_min_version': '*',
                'platform_max_version': '*',
                'platform_min_version': '9.0.0',
                'shell_commands': [],
                'version': '8.8.2'
            }
        }}
        self.assertDictEqual(expected, result)

    def test_validate_schema(self):
        xml = self._get_test_xml('data/infoxmls/invalid.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_fixes_xml(self):
        xml = self._get_test_xml('data/infoxmls/news.xml')
        parse_app_metadata(xml, self.config.info_schema,
                           self.config.pre_info_xslt,
                           self.config.info_xslt)

    def test_broken_xml(self):
        xml = self._get_test_xml('data/infoxmls/broken-xml.xml')
        with (self.assertRaises(APIException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_entities(self):
        xml = self._get_test_xml('data/infoxmls/entities.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_extract_contracts(self):
        path = self.get_path('data/archives/contacts.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        full_extracted, app_id = extractor.extract_app_metadata(path)
        self.assertEqual('contacts', app_id)

    def test_extract_gunzip_info(self):
        path = self.get_path('data/archives/full.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        full_extracted, app_id = extractor.extract_app_metadata(path)
        full = self._get_test_xml('data/infoxmls/full.xml')
        self.assertEqual(full, full_extracted)

    def test_extract_gunzip_no_appinfo(self):
        path = self.get_path('data/archives/invalid.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_no_single_app_folder(self):
        path = self.get_path('data/archives/multiplefolders.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_no_uppercase_app_folder(self):
        path = self.get_path('data/archives/invalidname.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_symlink(self):
        path = self.get_path('data/archives/symlink.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_appinfo_symlink(self):
        path = self.get_path('data/archives/appinfosymlink.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_app_symlink(self):
        path = self.get_path('data/archives/appsymlink.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path)

    def test_extract_zip(self):
        path = self.get_path('data/archives/empty.zip')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(UnsupportedAppArchiveException)):
            extractor.extract_app_metadata(path)

    def test_validate_english_name(self):
        xml = self._get_test_xml('data/infoxmls/no_en_name.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_validate_english_summary(self):
        xml = self._get_test_xml('data/infoxmls/no_en_summary.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_validate_english_description(self):
        xml = self._get_test_xml('data/infoxmls/no_en_description.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_map_data(self):
        full = self._get_test_xml('data/infoxmls/full.xml')
        result = parse_app_metadata(full, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        expected = {'app': {
            'id': 'news',
            'admin_docs': 'https://github.com/owncloud/news#readme',
            'categories': [
                {'category': {'id': 'multimedia'}},
                {'category': {'id': 'tools'}}
            ],
            'summary': {
                'en': 'An RSS/Atom feed reader',
            },
            'description': {
                'en': '#This is markdown',
                'de': 'Eine Nachrichten App, welche mit [RSS/Atom]('
                      'https://en.wikipedia.org/wiki/RSS) umgehen kann'
            },
            'developer_docs':
                'https://github.com/owncloud/news/wiki#developer'
                '-documentation',
            'user_docs': 'https://github.com/owncloud/news/wiki#user'
                         '-documentation',
            'website': 'https://github.com/owncloud/news',
            'discussion': 'https://help.nextcloud.com/t/news',
            'issue_tracker': 'https://github.com/owncloud/news/issues',
            'name': {'de': 'Nachrichten', 'en': 'News'},
            'release': {
                'databases': [
                    {'database': {
                        'id': 'pgsql',
                        'max_version': '*',
                        'min_version': '9.4.0'
                    }},
                    {'database': {
                        'id': 'sqlite',
                        'max_version': '*',
                        'min_version': '*'}},
                    {'database': {
                        'id': 'mysql',
                        'max_version': '*',
                        'min_version': '5.5.0'
                    }}
                ],
                'licenses': [
                    {'license': {'id': 'agpl'}}
                ],
                'min_int_size': 64,
                'php_extensions': [
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '2.7.8',
                        'id': 'libxml'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'id': 'curl'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'id': 'SimpleXML'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'id': 'iconv'
                    }}
                ],
                'php_max_version': '*',
                'php_min_version': '5.6.0',
                'platform_max_version': '9.2.0',
                'platform_min_version': '9.0.0',
                'shell_commands': [
                    {'shell_command': {'name': 'grep'}},
                    {'shell_command': {'name': 'ls'}}
                ],
                'version': '8.8.2'
            },
            'screenshots': [
                {'screenshot': {'url': 'https://example.com/1.png',
                                'ordering': 1}},
                {'screenshot': {'url': 'https://example.com/2.jpg',
                                'ordering': 2}}
            ],
        }}
        self.assertDictEqual(expected, result)

    def _get_test_xml(self, target):
        path = self.get_path(target)
        return read_file_contents(path)

    def get_path(self, target):
        return resolve_file_relative_path(__file__, target)
