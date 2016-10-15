import json
from copy import deepcopy

from django.test import TestCase
from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.api.v1.release.parser import \
    parse_app_metadata, GunZipAppMetadataExtractor, \
    InvalidAppPackageStructureException, \
    UnsupportedAppArchiveException, InvalidAppMetadataXmlException, \
    fix_partial_translations, parse_changelog, ForbiddenLinkException
from nextcloudappstore.core.facades import resolve_file_relative_path, \
    read_file_contents
from rest_framework.exceptions import APIException


class ParserTest(TestCase):
    def setUp(self):
        self.config = ReleaseConfig()
        self.maxDiff = None

    def test_parse_minimal(self):
        xml = self._get_contents('data/infoxmls/minimal.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        expected = {'app': {
            'id': 'news',
            'summary': {'en': 'An RSS/Atom feed reader'},
            'description': {'en': 'An RSS/Atom feed reader'},
            'authors': [{'author': {
                'homepage': None,
                'mail': None,
                'name': 'Bernhard Posselt'
            }}],
            'name': {'en': 'News'},
            'admin_docs': None,
            'developer_docs': None,
            'user_docs': None,
            'website': None,
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
                'raw_php_max_version': '*',
                'raw_php_min_version': '*',
                'platform_max_version': '*',
                'platform_min_version': '9.0.0',
                'raw_platform_max_version': '*',
                'raw_platform_min_version': '9',
                'shell_commands': [],
                'version': '8.8.2',
            },
            'ocsid': None,
        }}
        self.assertDictEqual(expected, result)

    def test_parse_repair_jobs(self):
        xml = self._get_contents('data/infoxmls/repair-and-jobs.xml')
        parse_app_metadata(xml, self.config.info_schema,
                           self.config.pre_info_xslt,
                           self.config.info_xslt)

    def test_parse_pre_release(self):
        xml = self._get_contents('data/infoxmls/prerelease.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        version = result['app']['release']['version']
        self.assertEqual('1.0.0-alpha.1', version)

    def test_parse_invalid_elements(self):
        xml = self._get_contents('data/infoxmls/invalid-elements.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_parse_minimal_transform(self):
        xml = self._get_contents('data/infoxmls/transform.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        min_version = result['app']['release']['platform_min_version']
        max_version = result['app']['release']['platform_max_version']
        self.assertEqual('10.0.0', min_version)
        self.assertEqual('12.0.0', max_version)

    def test_parse_minimal_nextcloud(self):
        xml = self._get_contents('data/infoxmls/nextcloud.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        min_version = result['app']['release']['platform_min_version']
        max_version = result['app']['release']['platform_max_version']
        self.assertEqual('10.0.0', min_version)
        self.assertEqual('12.0.0', max_version)

    def test_parse_category_mapping(self):
        xml = self._get_contents('data/infoxmls/category_mapping.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        categories = result['app']['categories']
        expected = [
            {'category': {'id': 'organization'}},
            {'category': {'id': 'tools'}},
        ]
        self.assertListEqual(expected, categories)

    def test_parse_category_mapping_tool(self):
        xml = self._get_contents('data/infoxmls/category_mapping_tool.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        categories = result['app']['categories']
        expected = [
            {'category': {'id': 'tools'}},
        ]
        self.assertListEqual(expected, categories)

    def test_parse_category_mapping_game(self):
        xml = self._get_contents('data/infoxmls/category_mapping_game.xml')
        result = parse_app_metadata(xml, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        categories = result['app']['categories']
        expected = [
            {'category': {'id': 'tools'}},
        ]
        self.assertListEqual(expected, categories)

    def test_validate_schema(self):
        xml = self._get_contents('data/infoxmls/invalid.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_fixes_xml(self):
        xml = self._get_contents('data/infoxmls/news.xml')
        parse_app_metadata(xml, self.config.info_schema,
                           self.config.pre_info_xslt,
                           self.config.info_xslt)

    def test_broken_xml(self):
        xml = self._get_contents('data/infoxmls/broken-xml.xml')
        with (self.assertRaises(APIException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_entities(self):
        xml = self._get_contents('data/infoxmls/entities.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_bad_shell(self):
        xml = self._get_contents('data/infoxmls/badcommand.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_extract_contracts(self):
        path = self.get_path('data/archives/contacts.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        full_extracted, app_id, changes = extractor.extract_app_metadata(path)
        self.assertEqual('contacts', app_id)
        self.assertEqual('', changes['en'])

    def test_extract_gunzip_info(self):
        path = self.get_path('data/archives/full.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        full_extracted, app_id, changes = extractor.extract_app_metadata(path)
        full = self._get_contents('data/infoxmls/full.xml')
        self.assertEqual(full, full_extracted)
        self.assertEqual('', changes['en'])

    def test_extract_changelog(self):
        path = self.get_path('data/archives/changelog.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        full_extracted, app_id, changes = extractor.extract_app_metadata(
            path)
        self.assertNotEqual('', changes)

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
        with (self.assertRaises(ForbiddenLinkException)):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_appinfo_symlink(self):
        path = self.get_path('data/archives/appinfosymlink.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(ForbiddenLinkException)):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_app_symlink(self):
        path = self.get_path('data/archives/appsymlink.tar.gz')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(ForbiddenLinkException)):
            extractor.extract_app_metadata(path)

    def test_extract_zip(self):
        path = self.get_path('data/archives/empty.zip')
        extractor = GunZipAppMetadataExtractor(self.config)
        with (self.assertRaises(UnsupportedAppArchiveException)):
            extractor.extract_app_metadata(path)

    def test_validate_english_name(self):
        xml = self._get_contents('data/infoxmls/no_en_name.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_validate_english_summary(self):
        xml = self._get_contents('data/infoxmls/no_en_summary.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_validate_english_description(self):
        xml = self._get_contents('data/infoxmls/no_en_description.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.config.info_schema,
                               self.config.pre_info_xslt,
                               self.config.info_xslt)

    def test_partial_translations(self):
        expected = {'app': {
            'name': {
                'en': 'Le name',
            },
            'summary': {
                'en': 'An RSS/Atom feed reader',
            },
            'description': {
                'en': '#This is markdown',
                'de': 'Eine Nachrichten App, welche mit [RSS/Atom]('
                      'https://en.wikipedia.org/wiki/RSS) umgehen kann'
            },
        }}
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertNotEqual(json.dumps(expected), json.dumps(result))
        self.assertEqual(result['app']['name']['de'], 'Le name')
        self.assertEqual(result['app']['summary']['de'],
                         'An RSS/Atom feed reader')
        self.assertEqual(result['app']['description']['de'],
                         'Eine Nachrichten App, welche mit [RSS/Atom]('
                         'https://en.wikipedia.org/wiki/RSS) umgehen kann')

    def test_partial_translations_not_all_present(self):
        expected = {'app': {
            'name': {
                'en': 'Le name',
            },
            'description': {
                'en': '#This is markdown',
                'de': 'Eine Nachrichten App, welche mit [RSS/Atom]('
                      'https://en.wikipedia.org/wiki/RSS) umgehen kann'
            },
        }}
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertNotEqual(json.dumps(expected), json.dumps(result))
        self.assertEqual(result['app']['name']['de'], 'Le name')
        self.assertTrue('summary' not in result['app'])
        self.assertEqual(result['app']['description']['de'],
                         'Eine Nachrichten App, welche mit [RSS/Atom]('
                         'https://en.wikipedia.org/wiki/RSS) umgehen kann')

    def test_partial_translations_no_change(self):
        expected = {'app': {
            'name': {
                'en': 'Le name',
                'de': 'B name',
            },
            'summary': {
                'en': 'An RSS/Atom feed reader',
                'de': 'An RSS/Atom feed reader',
            },
            'description': {
                'en': '#This is markdown',
                'de': 'Eine Nachrichten App, welche mit [RSS/Atom]('
                      'https://en.wikipedia.org/wiki/RSS) umgehen kann'
            },
        }}
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertDictEqual(expected, result)

    def test_partial_translations_no_change_not_all_present(self):
        expected = {'app': {
            'summary': {
                'en': 'An RSS/Atom feed reader',
                'de': 'An RSS/Atom feed reader',
            },
            'description': {
                'en': '#This is markdown',
                'de': 'Eine Nachrichten App, welche mit [RSS/Atom]('
                      'https://en.wikipedia.org/wiki/RSS) umgehen kann'
            },
        }}
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertDictEqual(expected, result)

    def test_map_data(self):
        full = self._get_contents('data/infoxmls/full.xml')
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
            'authors': [
                {'author': {
                    'homepage': 'http://example.com',
                    'mail': 'mail@provider.com',
                    'name': 'Bernhard Posselt'
                }},
                {'author': {
                    'homepage': None,
                    'mail': None,
                    'name': 'Alessandro Cosentino'
                }},
                {'author': {
                    'homepage': None,
                    'mail': None,
                    'name': 'Jan-Christoph Borchardt'
                }}
            ],
            'summary': {
                'en': 'An RSS/Atom feed reader',
                'de': 'An RSS/Atom feed reader',
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
            'issue_tracker': 'https://github.com/owncloud/news/issues',
            'name': {'de': 'Nachrichten', 'en': 'News'},
            'release': {
                'databases': [
                    {'database': {
                        'id': 'pgsql',
                        'max_version': '*',
                        'min_version': '9.4.0',
                        'raw_max_version': '*',
                        'raw_min_version': '9.4',
                    }},
                    {'database': {
                        'id': 'sqlite',
                        'max_version': '*',
                        'min_version': '*',
                        'raw_max_version': '*',
                        'raw_min_version': '*',
                    }},
                    {'database': {
                        'id': 'mysql',
                        'max_version': '*',
                        'min_version': '5.5.0',
                        'raw_max_version': '*',
                        'raw_min_version': '5.5',
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
                        'raw_max_version': '*',
                        'raw_min_version': '2.7.8',
                        'id': 'libxml'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'raw_max_version': '*',
                        'raw_min_version': '*',
                        'id': 'curl'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'raw_max_version': '*',
                        'raw_min_version': '*',
                        'id': 'SimpleXML'
                    }},
                    {'php_extension': {
                        'max_version': '*',
                        'min_version': '*',
                        'raw_max_version': '*',
                        'raw_min_version': '*',
                        'id': 'iconv'
                    }}
                ],
                'php_max_version': '*',
                'php_min_version': '5.6.0',
                'raw_php_max_version': '*',
                'raw_php_min_version': '5.6',
                'platform_max_version': '11.0.0',
                'platform_min_version': '9.0.0',
                'raw_platform_max_version': '10',
                'raw_platform_min_version': '9',
                'shell_commands': [
                    {'shell_command': {'name': 'grep'}},
                    {'shell_command': {'name': 'ls'}}
                ],
                'version': '8.8.2',
            },
            'screenshots': [
                {'screenshot': {'url': 'https://example.com/1.png',
                                'ordering': 1}},
                {'screenshot': {'url': 'https://example.com/2.jpg',
                                'ordering': 2}}
            ],
            'ocsid': None,
        }}
        self.assertDictEqual(expected, result)

    def test_parse_changelog_empty(self):
        changelog = parse_changelog('', '9.0')
        self.assertEqual('', changelog)

    def test_parse_changelog_not_found(self):
        file = self._get_contents('data/changelogs/CHANGELOG.md')
        changelog = parse_changelog(file, '0.3.2')
        self.assertEqual('', changelog)

    def test_parse_changelog(self):
        file = self._get_contents('data/changelogs/CHANGELOG.md')
        changelog = parse_changelog(file, '0.4.3')
        expected = self._get_contents('data/changelogs/0.4.3.md').strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_brackets(self):
        file = self._get_contents('data/changelogs/CHANGELOG.md')
        changelog = parse_changelog(file, '0.6.0')
        expected = self._get_contents('data/changelogs/0.6.0.md').strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_unstable(self):
        file = self._get_contents('data/changelogs/CHANGELOG.md')
        changelog = parse_changelog(file, '0.4.3-beta')
        expected = self._get_contents('data/changelogs/unreleased.md').strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_nightly(self):
        file = self._get_contents('data/changelogs/CHANGELOG.md')
        changelog = parse_changelog(file, '0.4.3', True)
        expected = self._get_contents('data/changelogs/unreleased.md').strip()
        self.assertEqual(expected, changelog)

    def _get_contents(self, target):
        path = self.get_path(target)
        return read_file_contents(path)

    def get_path(self, target):
        return resolve_file_relative_path(__file__, target)
