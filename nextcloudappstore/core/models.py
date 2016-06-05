from django.db import models
from django.utils.translation import ugettext_lazy as _


class App(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('Id'),
                          help_text=_('app id, same as the folder name'))
    categories = models.ManyToManyField('Category', verbose_name=_('Category'))
    authors = models.ManyToManyField('Author', verbose_name=_('Authors'))
    # possible l10n candidates
    name = models.CharField(max_length=128, verbose_name=_('Name'),
                            help_text=_('Rendered app name for users'))
    description = models.TextField(verbose_name=_('Description'),
                                   help_text=_('Will be rendered as Markdown'))
    # resources
    user_docs = models.URLField(max_length=256, blank=True,
                                verbose_name=_('User documentation url'))
    admin_docs = models.URLField(max_length=256, blank=True,
                                 verbose_name=_('Admin documentation url'))
    developer_docs = models.URLField(max_length=256, blank=True,
                                     verbose_name=_(
                                         'Developer documentation url'))
    issue_tracker = models.URLField(max_length=256, blank=True,
                                    verbose_name=_('Issue tracker url'))
    website = models.URLField(max_length=256, blank=True,
                              verbose_name=_('Homepage'))
    created = models.DateTimeField(auto_now_add=True, editable=False,
                                   verbose_name=_('Created at'))
    last_modified = models.DateTimeField(auto_now=True, editable=False,
                                         verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('App')
        verbose_name_plural = _('Apps')

    def __str__(self):
        return self.name


class AppRelease(models.Model):
    version = models.CharField(max_length=128, verbose_name=_('Version'),
                               help_text=_(
                                   'Version follows Semantic Versioning'))
    app = models.ForeignKey('App', on_delete=models.CASCADE,
                            verbose_name=_('App'))
    # dependencies
    libs = models.ManyToManyField('PhpExtension',
                                  through='PhpExtensionDependency',
                                  verbose_name=_('PHP extension dependency'))
    databases = models.ManyToManyField('Database',
                                       through='DatabaseDependency',
                                       verbose_name=_('Database dependency'))
    shell_commands = models.ManyToManyField('ShellCommand', verbose_name=_(
        'Shell command dependency'))
    php_min = models.CharField(max_length=32,
                               verbose_name=_('PHP minimum version'))
    php_max = models.CharField(max_length=32, blank=True,
                               verbose_name=_('PHP maximum version'))
    platform_min = models.CharField(max_length=32,
                                    verbose_name=_('Platform minimum version'))
    platform_max = models.CharField(max_length=32, blank=True,
                                    verbose_name=_('Platform maximum version'))
    download = models.URLField(max_length=256, blank=True,
                               verbose_name=_('Archive download Url'))
    created = models.DateTimeField(auto_now_add=True, editable=False,
                                   verbose_name=_('Created at'))
    last_modified = models.DateTimeField(auto_now=True, editable=False,
                                         verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('App Release')
        verbose_name_plural = _('App Releases')

    def __str__(self):
        return '%s %s' % (self.app, self.version)


class Screenshot(models.Model):
    url = models.URLField(max_length=256, verbose_name=_('Image url'))
    app = models.ForeignKey('App', on_delete=models.CASCADE,
                            verbose_name=_('App'))

    class Meta:
        verbose_name = _('Screenshot')
        verbose_name_plural = _('Screenshots')

    def __str__(self):
        return self.url


class Author(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Full name'))
    mail = models.EmailField(max_length=256, blank=True,
                             verbose_name=_('Mail address'))
    homepage = models.URLField(max_length=256, blank=True,
                               verbose_name=_('Homepage'))

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name


class ShellCommand(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text=_(
        'Name of a required shell command, e.g. grep'),
                            verbose_name=_('Shell Command'))

    class Meta:
        verbose_name = _('Shell Command')
        verbose_name_plural = _('Shell Commands')

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          help_text=_(
                              'Category id which is used to identify a '
                              'category. Used to identify categories when '
                              'uploading an app'), verbose_name=_('Id'))
    # possible l10n
    name = models.CharField(max_length=128, help_text=_(
        'Category name which will be presented to the user'),
                            verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Database(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('Id'),
                          help_text=_(
                              'Key which is used to identify a database'))
    # possible l10n
    name = models.CharField(max_length=128, verbose_name=_('Name'),
                            help_text=_(
                                'Database name which will be presented to '
                                'the user'))

    class Meta:
        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

    def __str__(self):
        return self.name


class DatabaseDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE,
                            verbose_name=_('App release'))
    database = models.ForeignKey('Database', on_delete=models.CASCADE,
                                 verbose_name=_('Database'))
    version_min = models.CharField(max_length=32,
                                   verbose_name=_('Database minimum version'))
    version_max = models.CharField(max_length=32, blank=True,
                                   verbose_name=_('Database maximum version'))

    class Meta:
        verbose_name = _('Database Dependency')
        verbose_name_plural = _('Database Dependencies')

    def __str__(self):
        return '%s: %s >=%s, <=%s' % (self.app_release, self.database,
                                      self.version_min, self.version_max)


class PhpExtension(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('PHP extension'),
                          help_text=_('e.g. libxml'))

    class Meta:
        verbose_name = _('PHP Extension')
        verbose_name_plural = _('PHP Extensions')

    def __str__(self):
        return self.id


class PhpExtensionDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE,
                                    verbose_name=_('App Release'))
    php_extension = models.ForeignKey('PhpExtension', on_delete=models.CASCADE,
                                      verbose_name=_('PHP Extension'))
    version_min = models.CharField(max_length=32,
                                   verbose_name=_('Extension minimum version'))
    version_max = models.CharField(max_length=32,
                                   verbose_name=_('Extension maximum version'),
                                   blank=True)

    class Meta:
        verbose_name = _('PHP Extension Dependency')
        verbose_name_plural = _('PHP Extension Dependencies')

    def __str__(self):
        return '%s: %s >=%s, <=%s' % (self.app_release.app, self.php_extension,
                                      self.version_min, self.version_max)
