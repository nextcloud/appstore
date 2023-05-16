from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from pymple import Container

from nextcloudappstore.api.v1.release import ReleaseConfig
from nextcloudappstore.api.v1.release.importer import AppImporter
from nextcloudappstore.api.v1.release.parser import parse_app_metadata
from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.core.models import App, Database, Screenshot


class ImporterTest(TestCase):
    def setUp(self):
        container = Container()
        self.importer = container.resolve(AppImporter)
        self.config = ReleaseConfig()
        self.min = read_relative_file(__file__, 'data/infoxmls/minimal.xml')
        self.full = read_relative_file(__file__,
                                       'data/infoxmls/fullimport.xml')
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='test',
                                                         email='test@test.com')
        self.app = App.objects.create(pk='news', owner=self.user)
        Screenshot.objects.create(url='https://google.com', ordering=1,
                                  app=self.app)

    def test_import_minimal(self):
        # check if translations are removed
        self.app.set_current_language('de')
        self.app.name = 'Should not exist'
        self.app.save()

        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self._assert_all_empty(app, ['user_docs', 'admin_docs', 'website',
                                     'developer_docs'])
        # l10n
        app.set_current_language('en')
        self.assertEqual('News', app.name)
        self.assertEqual('An RSS/Atom feed reader', app.description)
        app.set_current_language('de')  # fallback
        self.assertEqual('News', app.name)

        # authors
        self.assertEqual(1, app.authors.count())
        self.assertEqual('Bernhard Posselt', app.authors.all()[0].name)

        # categories
        self.assertEqual(1, app.categories.count())
        self.assertEqual('multimedia', app.categories.all()[0].id)

        self.assertEqual('https://github.com/nextcloud/news/issues',
                         app.issue_tracker)

        self.assertEqual(0, app.screenshots.count())
        self.assertEqual(0, Screenshot.objects.count())

        release = app.releases.all()[0]
        self.assertEqual(settings.CERTIFICATE_DIGEST, release.signature_digest)
        self.assertEqual('8.8.2', release.version)
        self.assertEqual('>=11.0.0,<13.0.0', release.platform_version_spec)
        self.assertEqual('*', release.php_version_spec)
        self.assertEqual('>=11,<=12', release.raw_platform_version_spec)
        self.assertEqual('*', release.raw_php_version_spec)
        self.assertEqual(32, release.min_int_size)
        self._assert_all_empty(release, ['signature', 'download'])
        self.assertEqual(0, release.php_extensions.count())
        self.assertEqual(0, release.databases.count())
        self.assertEqual(0, release.shell_commands.count())
        self.assertEqual(0, release.shell_commands.count())
        self.assertEqual(1, release.licenses.count())
        self.assertEqual('agpl', release.licenses.all()[0].id)

    def test_full(self):
        Database.objects.create(id='sqlite')
        Database.objects.create(id='pgsql')
        Database.objects.create(id='mysql')
        result = parse_app_metadata(self.full, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        # l10n
        app.set_current_language('en')
        self.assertEqual('https://github.com/owncloud/news', app.website)
        self.assertEqual('https://github.com/owncloud/disc', app.discussion)
        self.assertEqual(
            'https://github.com/owncloud/news/wiki#user-documentation',
            app.user_docs)
        self.assertEqual('News', app.name)
        self.assertEqual('An RSS/Atom feed reader', app.summary)
        self.assertEqual('#This is markdown', app.description)
        app.set_current_language('de')  # fallback
        self.assertEqual('Nachrichten', app.name)
        self.assertEqual(
            'Eine Nachrichten App, welche mit [RSS/Atom]('
            'https://en.wikipedia.org/wiki/RSS) umgehen kann',
            app.description)
        release = app.releases.all()[0]
        screenshots = app.screenshots.all()
        extensions = release.php_extensions.all()
        databases = release.databases.all()

        self.assertEqual(2, screenshots.count())
        self.assertEqual('https://example.com/1-thumb.png',
                         screenshots[0].small_thumbnail)
        self.assertEqual('', screenshots[1].small_thumbnail)
        self.assertEqual(3, databases.count())
        self.assertEqual(4, extensions.count())

        for db in databases:
            if db.id == 'sqlite':
                self.assertEqual('*',
                                 db.releasedependencies.get().version_spec)
                self.assertEqual('*',
                                 db.releasedependencies.get().raw_version_spec)
            elif db.id == 'pgsql':
                self.assertEqual('>=9.4.0',
                                 db.releasedependencies.get().version_spec)
                self.assertEqual('>=9.4',
                                 db.releasedependencies.get().raw_version_spec)
            elif db.id == 'mysql':
                self.assertEqual('>=5.5.0',
                                 db.releasedependencies.get().version_spec)
                self.assertEqual('>=5.5',
                                 db.releasedependencies.get().raw_version_spec)
        for ex in extensions:
            if ex.id == 'libxml':
                self.assertEqual('>=2.7.8',
                                 ex.releasedependencies.get().version_spec)
                self.assertEqual('>=2.7.8',
                                 ex.releasedependencies.get().raw_version_spec)
            elif ex.id in ['curl', 'SimpleXML', 'iconv']:
                self.assertEqual('*',
                                 ex.releasedependencies.get().version_spec)
                self.assertEqual('*',
                                 ex.releasedependencies.get().raw_version_spec)

    def test_release_update(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        result['app']['website'] = 'https://website.com'
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('https://website.com', app.website)

    def test_release_no_update(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        result['app']['website'] = 'https://website.com'
        result['app']['release']['version'] = '8.8.1'
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('', app.website)

    def test_release_no_update_prerelease(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        result['app']['website'] = 'https://website.com'
        result['app']['release']['version'] = '9.0.0-alpha'
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('', app.website)

    def test_release_no_update_nighly(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        self.importer.import_data('app', result['app'], None)
        result['app']['website'] = 'https://website.com'
        result['app']['release']['is_nightly'] = True
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('', app.website)

    def test_release_create_prerelease(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        result['app']['release']['version'] = '9.0.0-alpha'
        result['app']['website'] = 'https://website.com'
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('https://website.com', app.website)

    def test_release_create_nighly(self):
        result = parse_app_metadata(self.min, self.config.info_schema,
                                    self.config.pre_info_xslt,
                                    self.config.info_xslt)
        result['app']['release']['is_nightly'] = True
        result['app']['website'] = 'https://website.com'
        self.importer.import_data('app', result['app'], None)
        app = App.objects.get(pk='news')
        self.assertEqual('https://website.com', app.website)

    def _assert_all_empty(self, obj, attribs):
        for attrib in attribs:
            self.assertEqual('', getattr(obj, attrib), attrib)
