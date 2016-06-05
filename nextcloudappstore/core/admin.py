from django.contrib import admin
from nextcloudappstore.core.models import *

admin.site.register(App)
admin.site.register(AppRelease)
admin.site.register(Screenshot)
admin.site.register(Author)
admin.site.register(Command)
admin.site.register(Category)
admin.site.register(Database)
admin.site.register(DatabaseDependency)
admin.site.register(PhpLibrary)
admin.site.register(LibraryDependency)
