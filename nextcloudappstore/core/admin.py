from django.contrib import admin
from nextcloudappstore.core.models import *

admin.site.register(App)
admin.site.register(AppRelease)
admin.site.register(Screenshot)
admin.site.register(Author)
admin.site.register(ShellCommand)
admin.site.register(Category)
admin.site.register(Database)
admin.site.register(DatabaseDependency)
admin.site.register(PhpExtension)
admin.site.register(PhpExtensionDependency)
