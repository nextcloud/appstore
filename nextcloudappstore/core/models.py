from django.db import models
from django.utils.translation import ugettext_lazy as _


class App(models.Model):
    id = models.CharField(max_length=128, unique=True,
                          help_text=_('app id, same as the folder name'))
    categories = models.ManyToManyField(Category)
    authors = models.ManyToManyField(Author)
    # possible l10n candidates
    name = models.CharField(max_length=128)
    description = models.TextField()
    # resources
    user_docs = models.URLField(max_length=256, blank=True)
    admin_docs = models.URLField(max_length=256, blank=True)
    developer_docs = models.URLField(max_length=256, blank=True)
    issue_tracker = models.URLField(max_length=256, blank=True)
    website = models.URLField(max_length=256, blank=True)


class AppRelease(models.Model):
    version = models.CharField(max_length=128, unique=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    # dependencies
    libs = models.ManyToManyField(Library, through='LibraryDependency')
    databases = models.ManyToManyField(Database, through='DatabaseDependency')
    php_min = models.CharField(max_length=32)
    php_max = models.CharField(max_length=32, blank=True)
    platform_min = models.CharField(max_length=32)
    platform_max = models.CharField(max_length=32, blank=True)
    download = models.URLField(max_length=256, blank=True)


class Screenshot(models.Model):
    image = models.ImageField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=256)
    mail = models.EmailField(max_length=256, blank=True)
    homepage = models.URLField(max_length=256, blank=True)


class Command(models.Model):
    name = models.CharField(max_length=128, unique=True)


class Category(models.Model):
    id = models.CharField(max_length=128, unique=True)
    # possible l10n
    name = models.CharField(max_length=128, unique=True)


class Database(models.Model):
    id = models.CharField(max_length=128, unique=True)


class DatabaseDependency(models.Model):
    app = models.ForeignKey(AppRelease, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    version_min = models.CharField(max_length=32)
    version_max = models.CharField(max_length=32, blank=True)


class Library(models.Model):
    id = models.CharField(max_length=128, unique=True)


class LibraryDependency(models.Model):
    app_release = models.ForeignKey(AppRelease, on_delete=models.CASCADE)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    version_min = models.CharField(max_length=32)
    version_max = models.CharField(max_length=32, blank=True)
