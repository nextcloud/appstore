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


class AppRelease(models.Model):
    version = models.CharField(max_length=128)
    app = models.ForeignKey('App', on_delete=models.CASCADE)
    # dependencies
    libs = models.ManyToManyField('PhpLibrary', through='LibraryDependency')
    databases = models.ManyToManyField('Database',
                                       through='DatabaseDependency')
    php_min = models.CharField(max_length=32)
    php_max = models.CharField(max_length=32, blank=True)
    platform_min = models.CharField(max_length=32)
    platform_max = models.CharField(max_length=32, blank=True)
    download = models.URLField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Screenshot(models.Model):
    image = models.URLField(max_length=256)
    app = models.ForeignKey('App', on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=256)
    mail = models.EmailField(max_length=256, blank=True)
    homepage = models.URLField(max_length=256, blank=True)


class Command(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text=_(
        'Name of a required shell command, e.g. grep'))


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


class PhpLibrary(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True)


class LibraryDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE)
    library = models.ForeignKey('PhpLibrary', on_delete=models.CASCADE)
    version_min = models.CharField(max_length=32)
    version_max = models.CharField(max_length=32, blank=True)
