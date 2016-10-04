from typing import Dict, Any, Set, Tuple  # type: ignore
from django.utils import timezone
from semantic_version import Version  # type: ignore
from nextcloudappstore.core.models import App, Screenshot, Category, \
    AppRelease, ShellCommand, License, Database, DatabaseDependency, \
    PhpExtensionDependency, PhpExtension, AppAuthor
from nextcloudappstore.core.versioning import to_spec, to_raw_spec


def none_to_empty_string(value: str) -> str:
    if value is None:
        return ''
    else:
        return value


class Importer:
    def __init__(self, importers: Dict[str, 'Importer'],
                 ignored_fields: Set[str]) -> None:
        self.importers = importers
        self.ignored_fields = ignored_fields

    def import_data(self, key: str, value: Any, obj: Any) -> None:
        obj = self._get_object(key, value, obj)
        value, obj = self._before_import(key, value, obj)
        for key, val in value.items():
            if key not in self.ignored_fields:
                self.importers[key].import_data(key, val, obj)
        obj.save()

    def _get_object(self, key: str, value: Any, obj: Any) -> Any:
        raise NotImplementedError

    def _before_import(self, key: str, value: Any, obj: Any) -> Tuple[Any,
                                                                      Any]:
        raise NotImplementedError


class ScalarImporter(Importer):
    def __init__(self) -> None:
        super().__init__({}, set())


class PhpExtensionImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        for ext in value:
            version_spec = to_spec(ext['php_extension']['min_version'],
                                   ext['php_extension']['max_version'])
            raw_version_spec = to_raw_spec(
                ext['php_extension']['raw_min_version'],
                ext['php_extension']['raw_max_version'])
            extension, created = PhpExtension.objects.get_or_create(
                id=ext['php_extension']['id'])
            PhpExtensionDependency.objects.create(
                version_spec=version_spec,
                raw_version_spec=raw_version_spec,
                app_release=obj, php_extension=extension,
            )


class DatabaseImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        for db in value:
            version_spec = to_spec(db['database']['min_version'],
                                   db['database']['max_version'])
            raw_version_spec = to_raw_spec(db['database']['raw_min_version'],
                                           db['database']['raw_max_version'])
            # all dbs should be known already
            database = Database.objects.get(id=db['database']['id'])
            DatabaseDependency.objects.create(
                version_spec=version_spec,
                raw_version_spec=raw_version_spec,
                app_release=obj, database=database,
            )


class LicenseImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        def map_models(data: Dict) -> License:
            id = data['license']['id']
            model, created = License.objects.get_or_create(id=id)
            return model

        obj.licenses.set(list(map(map_models, value)))


class ShellCommandImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        def map_commands(data: Dict) -> ShellCommand:
            name = data['shell_command']['name']
            command, created = ShellCommand.objects.get_or_create(name=name)
            return command

        obj.shell_commands.set(list(map(map_commands, value)))


class AuthorImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        def map_authors(data: Dict) -> AppAuthor:
            author = data['author']
            return AppAuthor.objects.create(
                name=author['name'],
                mail=none_to_empty_string(author['mail']),
                homepage=none_to_empty_string(author['homepage'])
            )

        obj.authors.set(list(map(map_authors, value)))


class IntegerAttributeImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        setattr(obj, key, value)


class StringAttributeImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        setattr(obj, key, none_to_empty_string(value))


class MinVersionImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        setattr(obj, key, value)


class MaxVersionImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        setattr(obj, key, value)


class ScreenshotsImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        obj.screenshots.set(list(map(
            lambda img: Screenshot.objects.create(
                url=img['screenshot']['url'], app=obj,
                ordering=img['screenshot']['ordering']
            ), value
        )))


class CategoryImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        def map_categories(cat: Dict) -> Category:
            id = cat['category']['id']
            category, created = Category.objects.get_or_create(id=id)
            return category

        obj.categories.set(list(map(map_categories, value)))


class L10NImporter(ScalarImporter):
    def import_data(self, key: str, value: Any, obj: Any) -> None:
        for lang, translation in value.items():
            obj.set_current_language(lang)
            setattr(obj, key, translation)
            obj.save()


class AppReleaseImporter(Importer):
    def __init__(self, php_extension_importer: PhpExtensionImporter,
                 database_importer: DatabaseImporter,
                 license_importer: LicenseImporter,
                 shell_command_importer: ShellCommandImporter,
                 string_attribute_importer: StringAttributeImporter,
                 integer_attribute_importer: IntegerAttributeImporter) -> None:
        super().__init__({
            'php_extensions': php_extension_importer,
            'databases': database_importer,
            'licenses': license_importer,
            'php_version_spec': string_attribute_importer,
            'platform_version_spec': string_attribute_importer,
            'raw_php_version_spec': string_attribute_importer,
            'raw_platform_version_spec': string_attribute_importer,
            'min_int_size': integer_attribute_importer,
            'shell_commands': shell_command_importer,
            'signature': string_attribute_importer,
            'download': string_attribute_importer,
            'changelog': string_attribute_importer,
        }, {
            'version',
            'raw_version',
            'php_min_version',
            'php_max_version',
            'raw_php_min_version',
            'raw_php_max_version',
            'platform_min_version',
            'platform_max_version',
            'raw_platform_min_version',
            'raw_platform_max_version',
        })

    def _before_import(self, key: str, value: Any, obj: Any) -> Tuple[Any,
                                                                      Any]:
        # combine versions into specs
        value['platform_version_spec'] = to_spec(
            value['platform_min_version'], value['platform_max_version'])
        value['php_version_spec'] = to_spec(value['php_min_version'],
                                            value['php_max_version'])
        value['raw_platform_version_spec'] = to_raw_spec(
            value['raw_platform_min_version'],
            value['raw_platform_max_version'])
        value['raw_php_version_spec'] = to_raw_spec(
            value['raw_php_min_version'],
            value['raw_php_max_version'])
        obj.licenses.clear()
        obj.shell_commands.clear()
        obj.licenses.clear()
        obj.php_extensions.clear()
        obj.databases.clear()
        return value, obj

    def _get_object(self, key: str, value: Any, obj: Any) -> Any:
        release, created = AppRelease.objects.get_or_create(
            version=value['version'], app=obj
        )
        return release


class AppImporter(Importer):
    def __init__(self, release_importer: AppReleaseImporter,
                 screenshots_importer: ScreenshotsImporter,
                 attribute_importer: StringAttributeImporter,
                 l10n_importer: L10NImporter,
                 category_importer: CategoryImporter,
                 author_importer: AuthorImporter) -> None:
        super().__init__({
            'release': release_importer,
            'screenshots': screenshots_importer,
            'user_docs': attribute_importer,
            'admin_docs': attribute_importer,
            'website': attribute_importer,
            'discussion': attribute_importer,
            'developer_docs': attribute_importer,
            'issue_tracker': attribute_importer,
            'certificate': attribute_importer,
            'name': l10n_importer,
            'summary': l10n_importer,
            'description': l10n_importer,
            'categories': category_importer,
            'authors': author_importer
        }, {'id'})

    def _get_object(self, key: str, value: Any, obj: Any) -> Any:
        # only update app if newest or equal to newest release
        app, created = App.objects.get_or_create(pk=value['id'])
        return app

    def _before_import(self, key: str, value: Any, obj: Any) -> Tuple[Any,
                                                                      Any]:
        obj.last_release = timezone.now()
        # only new releases update an app's data
        if not self._is_latest_version(value):
            value = {'id': value['id'], 'release': value['release']}
        else:
            # clear all relations
            obj.screenshots.all().delete()
            obj.authors.all().delete()
            obj.categories.clear()
            for translation in obj.translations.all():
                translation.delete()
        if value['release']['version'].endswith('-nightly'):
            AppRelease.objects.filter(
                app__id=obj.id, version__endswith='-nightly').delete()
        return value, obj

    def _is_latest_version(self, value: Any) -> bool:
        releases = AppRelease.objects.filter(app__id=value['id'])
        uploaded_version = Version(value['release']['version'])
        for release in releases:
            if uploaded_version < Version(release.version):
                return False
        return True
