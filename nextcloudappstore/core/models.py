from django.conf import settings  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.db.models import ManyToManyField, ForeignKey, \
    URLField, IntegerField, CharField, CASCADE, TextField, \
    DateTimeField, Model, BooleanField  # type: ignore
from django.utils.translation import ugettext_lazy as _  # type: ignore
from parler.models import TranslatedFields, TranslatableModel  # type: ignore


class App(TranslatableModel):
    id = CharField(max_length=128, unique=True, primary_key=True,
                   verbose_name=_('Id'),
                   help_text=_('app id, identical to folder name'))
    categories = ManyToManyField('Category', verbose_name=_('Category'))
    translations = TranslatedFields(
        name=CharField(max_length=128, verbose_name=_('Name'),
                       help_text=_('Rendered app name for users')),
        description=TextField(verbose_name=_('Description'), help_text=_(
            'Will be rendered as Markdown'))
    )
    # resources
    user_docs = URLField(max_length=256, blank=True,
                         verbose_name=_('User documentation url'))
    admin_docs = URLField(max_length=256, blank=True,
                          verbose_name=_('Admin documentation url'))
    developer_docs = URLField(max_length=256, blank=True,
                              verbose_name=_('Developer documentation url'))
    issue_tracker = URLField(max_length=256, blank=True,
                             verbose_name=_('Issue tracker url'))
    website = URLField(max_length=256, blank=True, verbose_name=_('Homepage'))
    created = DateTimeField(auto_now_add=True, editable=False,
                            verbose_name=_('Created at'))
    last_modified = DateTimeField(auto_now=True, editable=False,
                                  verbose_name=_('Updated at'))
    owner = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('App owner'),
                       on_delete=CASCADE, related_name='owned_apps')
    co_maintainers = ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                     verbose_name=_('Co-Maintainers'),
                                     related_name='co_maintained_apps')
    recommendations = ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                      verbose_name=_('Recommendations'),
                                      related_name='recommended_apps')
    featured = BooleanField(verbose_name=_('Featured'), default=False)

    class Meta:
        verbose_name = _('App')
        verbose_name_plural = _('Apps')

    def __str__(self) -> str:
        return self.name

    def can_update(self, user: User) -> bool:
        return self.owner == user or user in self.co_maintainers.all()

    def can_delete(self, user: User) -> bool:
        return self.owner == user


class AppRelease(Model):
    version = CharField(max_length=128, verbose_name=_('Version'),
                        help_text=_('Version follows Semantic Versioning'))
    app = ForeignKey('App', on_delete=CASCADE, verbose_name=_('App'),
                     related_name='releases')
    # dependencies
    php_extensions = ManyToManyField('PhpExtension', blank=True,
                                     through='PhpExtensionDependency',
                                     verbose_name=_(
                                         'PHP extension dependency'))
    databases = ManyToManyField('Database', blank=True,
                                through='DatabaseDependency',
                                verbose_name=_('Database dependency'))
    licenses = ManyToManyField('License', verbose_name=_('License'))
    shell_commands = ManyToManyField('ShellCommand', blank=True,
                                     verbose_name=_(
                                         'Shell command dependency'))
    php_version_spec = CharField(max_length=128,
                                 verbose_name=_('PHP version requirement'))
    platform_version_spec = CharField(max_length=128, verbose_name=_(
        'Platform version requirement'))
    min_int_size = IntegerField(blank=True, default=32,
                                verbose_name=_('Minimum Integer Bits'),
                                help_text=_('e.g. 32 for 32bit Integers'))
    checksum = CharField(max_length=64, verbose_name=_('SHA256 checksum'))
    download = URLField(max_length=256, blank=True,
                        verbose_name=_('Archive download Url'))
    created = DateTimeField(auto_now_add=True, editable=False,
                            verbose_name=_('Created at'))
    last_modified = DateTimeField(auto_now=True, editable=False,
                                  verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('App Release')
        verbose_name_plural = _('App Releases')
        unique_together = (('app', 'version'),)
        ordering = ['-version']

    def can_update(self, user: User) -> bool:
        return self.app.owner == user or user in self.app.co_maintainers.all()

    def can_delete(self, user: User) -> bool:
        return self.can_update(user)

    def __str__(self) -> str:
        return '%s %s' % (self.app, self.version)


class Screenshot(Model):
    url = URLField(max_length=256, verbose_name=_('Image url'))
    app = ForeignKey('App', on_delete=CASCADE, verbose_name=_('App'),
                     related_name='screenshots')
    ordering = IntegerField(verbose_name=_('Ordering'))

    class Meta:
        verbose_name = _('Screenshot')
        verbose_name_plural = _('Screenshots')
        ordering = ['ordering']

    def __str__(self) -> str:
        return self.url


class ShellCommand(Model):
    name = CharField(max_length=128, unique=True, primary_key=True,
                     verbose_name=_('Shell Command'),
                     help_text=_(
                         'Name of a required shell command, e.g. grep'))

    class Meta:
        verbose_name = _('Shell Command')
        verbose_name_plural = _('Shell Commands')

    def __str__(self) -> str:
        return self.name


class Category(TranslatableModel):
    id = CharField(max_length=128, unique=True, primary_key=True,
                   verbose_name=_('Id'),
                   help_text=_(
                       'Category id which is used to identify a '
                       'category. Used to identify categories when '
                       'uploading an app'))
    created = DateTimeField(auto_now_add=True, editable=False,
                            verbose_name=_('Created at'))
    last_modified = DateTimeField(auto_now=True, editable=False,
                                  verbose_name=_('Updated at'))
    translations = TranslatedFields(
        name=CharField(max_length=128, help_text=_(
            'Category name which will be presented to the user'),
                       verbose_name=_('Name')),
        description=TextField(verbose_name=_('Description'),
                              help_text=_('Will be rendered as Markdown'))
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self) -> str:
        return self.name


class License(Model):
    id = CharField(max_length=128, unique=True, primary_key=True,
                   verbose_name=_('Id'),
                   help_text=_(
                       'Key which is used to identify a license'))
    name = CharField(max_length=128, verbose_name=_('Name'),
                     help_text=_(
                         'License name which will be presented to '
                         'the user'))

    class Meta:
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')

    def __str__(self) -> str:
        return self.name


class Database(Model):
    id = CharField(max_length=128, unique=True, primary_key=True,
                   verbose_name=_('Id'),
                   help_text=_('Key which is used to identify a database'))
    name = CharField(max_length=128, verbose_name=_('Name'),
                     help_text=_(
                         'Database name which will be presented to the user'))

    class Meta:
        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

    def __str__(self) -> str:
        return self.name


class DatabaseDependency(Model):
    app_release = ForeignKey('AppRelease', on_delete=CASCADE,
                             verbose_name=_('App release'),
                             related_name='databasedependencies')
    database = ForeignKey('Database', related_name='releasedependencies',
                          on_delete=CASCADE, verbose_name=_('Database'))
    version_spec = CharField(max_length=128,
                             verbose_name=_('Database version requirement'))

    class Meta:
        verbose_name = _('Database Dependency')
        verbose_name_plural = _('Database Dependencies')
        unique_together = (('app_release', 'database', 'version_spec'),)

    def __str__(self) -> str:
        return '%s: %s %s' % (self.app_release, self.database,
                              self.version_spec)


class PhpExtension(Model):
    id = CharField(max_length=128, unique=True, help_text=_('e.g. libxml'),
                   primary_key=True, verbose_name=_('PHP extension'))

    class Meta:
        verbose_name = _('PHP Extension')
        verbose_name_plural = _('PHP Extensions')

    def __str__(self) -> str:
        return self.id


class PhpExtensionDependency(Model):
    app_release = ForeignKey('AppRelease', on_delete=CASCADE,
                             verbose_name=_('App Release'),
                             related_name='phpextensiondependencies')
    php_extension = ForeignKey('PhpExtension', on_delete=CASCADE,
                               verbose_name=_('PHP Extension'),
                               related_name='releasedependencies')
    version_spec = CharField(max_length=128,
                             verbose_name=_('Extension version requirement'))

    class Meta:
        verbose_name = _('PHP Extension Dependency')
        verbose_name_plural = _('PHP Extension Dependencies')
        unique_together = (('app_release', 'php_extension', 'version_spec'),)

    def __str__(self) -> str:
        return '%s: %s %s' % (self.app_release.app, self.php_extension,
                              self.version_spec)
