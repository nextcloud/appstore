import json
from copy import deepcopy

from django.test import TestCase
from rest_framework.exceptions import ParseError

from nextcloudappstore.api.v1.release import ReleaseConfig
from nextcloudappstore.api.v1.release.parser import (
    BlacklistedMemberException,
    ForbiddenLinkException,
    GunZipAppMetadataExtractor,
    InvalidAppMetadataXmlException,
    InvalidAppPackageStructureException,
    UnsupportedAppArchiveException,
    fix_partial_translations,
    parse_app_metadata,
    parse_changelog,
    validate_database,
)
from nextcloudappstore.core.facades import (
    read_file_contents,
    resolve_file_relative_path,
)


class ParserTest(TestCase):
    def setUp(self):
        self.config = ReleaseConfig()
        self.maxDiff = None

    def test_parse_minimal(self):
        xml = self._get_contents("data/infoxmls/minimal.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        expected = {
            "app": {
                "id": "news",
                "summary": {"en": "An RSS/Atom feed reader"},
                "description": {"en": "An RSS/Atom feed reader"},
                "authors": [{"author": {"homepage": None, "mail": None, "name": "Bernhard Posselt"}}],
                "name": {"en": "News"},
                "discussion": None,
                "website": None,
                "issue_tracker": "https://github.com/nextcloud/news/issues",
                "screenshots": [],
                "categories": [{"category": {"id": "multimedia"}}],
                "release": {
                    "databases": [],
                    "licenses": [{"license": {"id": "agpl"}}],
                    "min_int_size": 32,
                    "php_extensions": [],
                    "php_max_version": "*",
                    "php_min_version": "*",
                    "raw_php_max_version": "*",
                    "raw_php_min_version": "*",
                    "platform_max_version": "13.0.0",
                    "platform_min_version": "11.0.0",
                    "raw_platform_max_version": "12",
                    "raw_platform_min_version": "11",
                    "shell_commands": [],
                    "version": "8.8.2",
                },
            }
        }
        self.assertDictEqual(expected, result)

    def test_parse_repair_jobs(self):
        xml = self._get_contents("data/infoxmls/repair-and-jobs.xml")
        parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_parse_settings_and_activity_and_nav(self):
        xml = self._get_contents("data/infoxmls/settings-and-activity-and-nav.xml")
        parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_parse_collaboration(self):
        xml = self._get_contents("data/infoxmls/collaboration.xml")
        parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_parse_sabre(self):
        xml = self._get_contents("data/infoxmls/sabre.xml")
        parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_parse_pre_release(self):
        xml = self._get_contents("data/infoxmls/prerelease.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        version = result["app"]["release"]["version"]
        self.assertEqual("1.0.0-alpha.1", version)

    def test_parse_digit_id(self):
        xml = self._get_contents("data/infoxmls/digits.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        self.assertEqual("twofactor_u2f", result["app"]["id"])

    def test_parse_invalid_elements(self):
        xml = self._get_contents("data/infoxmls/invalid-elements.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_parse_invalid_archive(self):
        path = self.get_path("data/archives/notgzipped.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(UnsupportedAppArchiveException):
            extractor.extract_app_metadata(path)

    def test_parse_minimal_nextcloud(self):
        xml = self._get_contents("data/infoxmls/nextcloud.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        min_version = result["app"]["release"]["platform_min_version"]
        max_version = result["app"]["release"]["platform_max_version"]
        self.assertEqual("10.0.0", min_version)
        self.assertEqual("12.0.0", max_version)

    def test_parse_non_doc_urls(self):
        xml = self._get_contents("data/infoxmls/nondocurls.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        self.assertNotIn("admin_docs", result["app"])
        self.assertNotIn("developer_docs", result["app"])
        self.assertNotIn("user_docs", result["app"])

    def test_parse_switched_non_doc_urls(self):
        xml = self._get_contents("data/infoxmls/switchednondocurls.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_changes_auth_to_security_category(self):
        xml = self._get_contents("data/infoxmls/authmigration.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        self.assertEqual("security", result["app"]["categories"][0]["category"]["id"])

    def test_validate_schema(self):
        xml = self._get_contents("data/infoxmls/invalid.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_fixes_xml(self):
        xml = self._get_contents("data/infoxmls/news.xml")
        parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_broken_xml(self):
        xml = self._get_contents("data/infoxmls/broken-xml.xml")
        with self.assertRaises(ParseError):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_entities(self):
        xml = self._get_contents("data/infoxmls/entities.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_bad_shell(self):
        xml = self._get_contents("data/infoxmls/badcommand.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_extract_contacts(self):
        path = self.get_path("data/archives/contacts.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        meta = extractor.extract_app_metadata(path)
        self.assertEqual("contacts", meta.app_id)
        self.assertEqual("", meta.changelog["en"])

    def test_extract_u2f(self):
        path = self.get_path("data/archives/twofactor_u2f.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        meta = extractor.extract_app_metadata(path)
        self.assertEqual("twofactor_u2f", meta.app_id)

    def test_extract_gunzip_info(self):
        path = self.get_path("data/archives/full.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        meta = extractor.extract_app_metadata(path)
        full = self._get_contents("data/infoxmls/full.xml")
        self.assertEqual(full, meta.info_xml)
        self.assertEqual("", meta.changelog["en"])
        self.assertEqual("", meta.database_xml)

    def test_extract_changelog(self):
        path = self.get_path("data/archives/changelog.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        meta = extractor.extract_app_metadata(path)
        self.assertNotEqual("", meta.changelog)

    def test_extract_database(self):
        path = self.get_path("data/archives/database.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        meta = extractor.extract_app_metadata(path)
        self.assertNotEqual("his", meta.changelog)

    def test_invalid_files(self):
        path = self.get_path("data/archives/blacklisted_files.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(BlacklistedMemberException):
            extractor.extract_app_metadata(path)

    def test_invalid_directories(self):
        path = self.get_path("data/archives/blacklisted_directories.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(BlacklistedMemberException):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_no_appinfo(self):
        path = self.get_path("data/archives/invalid.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(InvalidAppPackageStructureException):
            extractor.extract_app_metadata(path)

    def test_extract_no_single_app_folder(self):
        path = self.get_path("data/archives/multiplefolders.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(InvalidAppPackageStructureException):
            extractor.extract_app_metadata(path)

    def test_extract_no_uppercase_app_folder(self):
        path = self.get_path("data/archives/invalidname.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(InvalidAppPackageStructureException):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_symlink(self):
        path = self.get_path("data/archives/symlink.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(ForbiddenLinkException):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_appinfo_symlink(self):
        path = self.get_path("data/archives/appinfosymlink.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(ForbiddenLinkException):
            extractor.extract_app_metadata(path)

    def test_extract_gunzip_app_symlink(self):
        path = self.get_path("data/archives/appsymlink.tar.gz")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(ForbiddenLinkException):
            extractor.extract_app_metadata(path)

    def test_extract_zip(self):
        path = self.get_path("data/archives/empty.zip")
        extractor = GunZipAppMetadataExtractor(self.config)
        with self.assertRaises(UnsupportedAppArchiveException):
            extractor.extract_app_metadata(path)

    def test_validate_english_name(self):
        xml = self._get_contents("data/infoxmls/no_en_name.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_validate_broken_database(self):
        xml = self._get_contents("data/database/broken.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_db_elements_database(self):
        xml = self._get_contents("data/database/invaliddb.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_table_elements_database(self):
        xml = self._get_contents("data/database/invalidtable.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_declaration_elements_database(self):
        xml = self._get_contents("data/database/invaliddeclaration.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_name_before_decl_database(self):
        xml = self._get_contents("data/database/nameafterdecl.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_field_elements_database(self):
        xml = self._get_contents("data/database/invalidfield.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_index_elements_database(self):
        xml = self._get_contents("data/database/invalidindex.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_invalid_indexfield_elements_database(self):
        xml = self._get_contents("data/database/invalidindexfield.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_news_database(self):
        xml = self._get_contents("data/database/news.xml")
        validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_server_database(self):
        xml = self._get_contents("data/database/server.xml")
        validate_database(xml, self.config.db_schema, self.config.pre_db_xslt)

    def test_validate_english_summary(self):
        xml = self._get_contents("data/infoxmls/no_en_summary.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_validate_english_description(self):
        xml = self._get_contents("data/infoxmls/no_en_description.xml")
        with self.assertRaises(InvalidAppMetadataXmlException):
            parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)

    def test_partial_translations(self):
        expected = {
            "app": {
                "name": {
                    "en": "Le name",
                },
                "summary": {
                    "en": "An RSS/Atom feed reader",
                },
                "description": {
                    "en": "#This is markdown",
                    "de": "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
                },
            }
        }
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertNotEqual(json.dumps(expected), json.dumps(result))
        self.assertEqual(result["app"]["name"]["de"], "Le name")
        self.assertEqual(result["app"]["summary"]["de"], "An RSS/Atom feed reader")
        self.assertEqual(
            result["app"]["description"]["de"],
            "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
        )

    def test_partial_translations_not_all_present(self):
        expected = {
            "app": {
                "name": {
                    "en": "Le name",
                },
                "description": {
                    "en": "#This is markdown",
                    "de": "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
                },
            }
        }
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertNotEqual(json.dumps(expected), json.dumps(result))
        self.assertEqual(result["app"]["name"]["de"], "Le name")
        self.assertTrue("summary" not in result["app"])
        self.assertEqual(
            result["app"]["description"]["de"],
            "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
        )

    def test_partial_translations_no_change(self):
        expected = {
            "app": {
                "name": {
                    "en": "Le name",
                    "de": "B name",
                },
                "summary": {
                    "en": "An RSS/Atom feed reader",
                    "de": "An RSS/Atom feed reader",
                },
                "description": {
                    "en": "#This is markdown",
                    "de": "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
                },
            }
        }
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertDictEqual(expected, result)

    def test_partial_translations_no_change_not_all_present(self):
        expected = {
            "app": {
                "summary": {
                    "en": "An RSS/Atom feed reader",
                    "de": "An RSS/Atom feed reader",
                },
                "description": {
                    "en": "#This is markdown",
                    "de": "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
                },
            }
        }
        result = deepcopy(expected)
        fix_partial_translations(result)
        self.assertDictEqual(expected, result)

    def test_map_data(self):
        full = self._get_contents("data/infoxmls/full.xml")
        result = parse_app_metadata(full, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        expected = {
            "app": {
                "id": "news",
                "admin_docs": "https://github.com/owncloud/news#readme",
                "categories": [{"category": {"id": "multimedia"}}, {"category": {"id": "tools"}}],
                "authors": [
                    {
                        "author": {
                            "homepage": "http://example.com",
                            "mail": "mail@provider.com",
                            "name": "Bernhard Posselt",
                        }
                    },
                    {"author": {"homepage": None, "mail": None, "name": "Alessandro Cosentino"}},
                    {"author": {"homepage": None, "mail": None, "name": "Jan-Christoph Borchardt"}},
                ],
                "summary": {
                    "en": "An RSS/Atom feed reader",
                    "de": "An RSS/Atom feed reader",
                },
                "description": {
                    "en": "#This is markdown",
                    "de": "Eine Nachrichten App, welche mit [RSS/Atom](https://en.wikipedia.org/wiki/RSS) umgehen kann",
                },
                "developer_docs": "https://github.com/owncloud/news/wiki#developer-documentation",
                "user_docs": "https://github.com/owncloud/news/wiki#user-documentation",
                "website": "https://github.com/owncloud/news",
                "discussion": "https://help.nextcloud.com/t/news/1",
                "issue_tracker": "https://github.com/owncloud/news/issues",
                "name": {"de": "Nachrichten", "en": "News"},
                "release": {
                    "databases": [
                        {
                            "database": {
                                "id": "pgsql",
                                "max_version": "*",
                                "min_version": "9.4.0",
                                "raw_max_version": "*",
                                "raw_min_version": "9.4",
                            }
                        },
                        {
                            "database": {
                                "id": "sqlite",
                                "max_version": "*",
                                "min_version": "*",
                                "raw_max_version": "*",
                                "raw_min_version": "*",
                            }
                        },
                        {
                            "database": {
                                "id": "mysql",
                                "max_version": "*",
                                "min_version": "5.5.0",
                                "raw_max_version": "*",
                                "raw_min_version": "5.5",
                            }
                        },
                    ],
                    "licenses": [{"license": {"id": "agpl"}}],
                    "min_int_size": 64,
                    "php_extensions": [
                        {
                            "php_extension": {
                                "max_version": "*",
                                "min_version": "2.7.8",
                                "raw_max_version": "*",
                                "raw_min_version": "2.7.8",
                                "id": "libxml",
                            }
                        },
                        {
                            "php_extension": {
                                "max_version": "*",
                                "min_version": "*",
                                "raw_max_version": "*",
                                "raw_min_version": "*",
                                "id": "curl",
                            }
                        },
                        {
                            "php_extension": {
                                "max_version": "*",
                                "min_version": "*",
                                "raw_max_version": "*",
                                "raw_min_version": "*",
                                "id": "SimpleXML",
                            }
                        },
                        {
                            "php_extension": {
                                "max_version": "*",
                                "min_version": "*",
                                "raw_max_version": "*",
                                "raw_min_version": "*",
                                "id": "iconv",
                            }
                        },
                    ],
                    "php_max_version": "*",
                    "php_min_version": "5.6.0",
                    "raw_php_max_version": "*",
                    "raw_php_min_version": "5.6",
                    "platform_max_version": "11.0.0",
                    "platform_min_version": "9.0.0",
                    "raw_platform_max_version": "10",
                    "raw_platform_min_version": "9",
                    "shell_commands": [{"shell_command": {"name": "grep"}}, {"shell_command": {"name": "ls"}}],
                    "version": "8.8.2",
                },
                "screenshots": [
                    {"screenshot": {"url": "https://example.com/1.png", "small_thumbnail": None, "ordering": 1}},
                    {"screenshot": {"url": "https://example.com/2.jpg", "small_thumbnail": None, "ordering": 2}},
                ],
            }
        }
        self.assertDictEqual(expected, result)

    def test_parse_changelog_empty(self):
        changelog = parse_changelog("", "9.0")
        self.assertEqual("", changelog)
        for changelog_path in ("data/changelogs/CHANGELOG.md", "data/changelogs/CHANGELOG_v.md"):
            file = self._get_contents(changelog_path)
            changelog = parse_changelog(file, "0.3")
            self.assertEqual("", changelog)

    def test_parse_changelog_not_found(self):
        file = self._get_contents("data/changelogs/CHANGELOG.md")
        changelog = parse_changelog(file, "0.3.2")
        self.assertEqual("", changelog)

    def test_parse_changelog(self):
        file = self._get_contents("data/changelogs/CHANGELOG.md")
        changelog = parse_changelog(file, "0.4.3")
        expected = self._get_contents("data/changelogs/0.4.3.md").strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_brackets(self):
        file = self._get_contents("data/changelogs/CHANGELOG.md")
        changelog = parse_changelog(file, "0.6.0")
        expected = self._get_contents("data/changelogs/0.6.0.md").strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_unstable(self):
        file = self._get_contents("data/changelogs/CHANGELOG.md")
        changelog = parse_changelog(file, "0.4.3-beta")
        expected = self._get_contents("data/changelogs/unreleased.md").strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_nightly(self):
        file = self._get_contents("data/changelogs/CHANGELOG.md")
        changelog = parse_changelog(file, "0.4.3", True)
        expected = self._get_contents("data/changelogs/unreleased.md").strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_prefix_v(self):
        file = self._get_contents("data/changelogs/CHANGELOG_v.md")
        changelog = parse_changelog(file, "0.4.3")
        expected = self._get_contents("data/changelogs/0.4.3.md").strip()
        self.assertEqual(expected, changelog)

    def test_parse_changelog_brackets_prefix_v(self):
        file = self._get_contents("data/changelogs/CHANGELOG_v.md")
        changelog = parse_changelog(file, "0.6.0")
        expected = self._get_contents("data/changelogs/0.6.0.md").strip()
        self.assertEqual(expected, changelog)

    def test_appapi(self):
        xml = self._get_contents("data/infoxmls/app_api.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        assert result["app"]["release"]["version"] == "2.0.0"
        r_ex_app = result["app"]["release"]["external_app"]
        assert r_ex_app["docker_install"] == {
            "image": "cloud-py-api/skeleton",
            "image_tag": "1.0.0",
            "registry": "ghcr.io",
        }
        assert r_ex_app["scopes"] == [{"value": "FILES"}, {"value": "NOTIFICATIONS"}, {"value": "TALK"}]
        assert r_ex_app["system"] == "true"

    def test_appapi_minimal(self):
        xml = self._get_contents("data/infoxmls/app_api_minimal.xml")
        result = parse_app_metadata(xml, self.config.info_schema, self.config.pre_info_xslt, self.config.info_xslt)
        assert result["app"]["release"]["version"] == "1.0.0"
        r_ex_app = result["app"]["release"]["external_app"]
        assert r_ex_app["docker_install"] == {
            "image": "cloud-py-api/skeleton",
            "image_tag": "latest",
            "registry": "ghcr.io",
        }
        assert r_ex_app["scopes"] == []

    def _get_contents(self, target):
        path = self.get_path(target)
        return read_file_contents(path)

    def get_path(self, target):
        return resolve_file_relative_path(__file__, target)
