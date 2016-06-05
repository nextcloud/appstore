from django.db import models
from django.utils.translation import ugettext_lazy as _


class App(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          help_text=_('app id, same as the folder name'))
    categories = models.ManyToManyField('Category')
    authors = models.ManyToManyField('Author')
    # possible l10n candidates
    name = models.CharField(max_length=128)
    description = models.TextField()
    # resources
    user_docs = models.URLField(max_length=256, blank=True)
    admin_docs = models.URLField(max_length=256, blank=True)
    developer_docs = models.URLField(max_length=256, blank=True)
    issue_tracker = models.URLField(max_length=256, blank=True)
    website = models.URLField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('App')
        verbose_name_plural = _('Apps')

    def __str__(self):
        return self.name


class AppRelease(models.Model):
    version = models.CharField(max_length=128)
    app = models.ForeignKey('App', on_delete=models.CASCADE)
    # dependencies
    libs = models.ManyToManyField('PhpExtension',
                                  through='PhpExtensionDependency')
    databases = models.ManyToManyField('Database',
                                       through='DatabaseDependency')
    shell_commands = models.ManyToManyField('ShellCommand')
    php_min = models.CharField(max_length=32)
    php_max = models.CharField(max_length=32, blank=True)
    platform_min = models.CharField(max_length=32)
    platform_max = models.CharField(max_length=32, blank=True)
    download = models.URLField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('App Release')
        verbose_name_plural = _('App Releases')

    def __str__(self):
        return '%s %s' % (self.app, self.version)


class Screenshot(models.Model):
    url = models.URLField(max_length=256)
    app = models.ForeignKey('App', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Screenshot')
        verbose_name_plural = _('Screenshots')

    def __str__(self):
        return self.url


class Author(models.Model):
    name = models.CharField(max_length=256)
    mail = models.EmailField(max_length=256, blank=True)
    homepage = models.URLField(max_length=256, blank=True)

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name


class ShellCommand(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text=_(
        'Name of a required shell command, e.g. grep'))

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
                              'uploading an app'))
    # possible l10n
    name = models.CharField(max_length=128, help_text=_(
        'Category name which will be presented to the user'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Database(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          help_text=_(
                              'Key which is used to identify a database'))
    # possible l10n
    name = models.CharField(max_length=128, help_text=_(
        'Database name which will be presented to the user'))

    class Meta:
        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

    def __str__(self):
        return self.name


class DatabaseDependency(models.Model):
    app = models.ForeignKey('AppRelease', on_delete=models.CASCADE)
    database = models.ForeignKey('Database', on_delete=models.CASCADE)
    version_min = models.CharField(max_length=32)
    version_max = models.CharField(max_length=32, blank=True)


class PhpExtension(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True)

    class Meta:
        verbose_name = _('PHP Extension')
        verbose_name_plural = _('PHP Extensions')

    def __str__(self):
        return self.id


class PhpExtensionDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE)
    php_extension = models.ForeignKey('PhpExtension', on_delete=models.CASCADE)
    version_min = models.CharField(max_length=32)
    version_max = models.CharField(max_length=32, blank=True)

    class Meta:
        verbose_name = _('PHP Extension Dependency')
        verbose_name_plural = _('PHP Extension Dependencies')

    def __str__(self):
        return '%s: %s >=%s, <=%s' % (self.app_release.app, self.php_extension,
                                      self.version_min, self.version_max)
