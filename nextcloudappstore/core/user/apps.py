from django.apps import AppConfig
from django.utils.translation import ugettext as _


class UserConfig(AppConfig):
    name = 'nextcloudappstore.core.user'
    verbose_name = _('App Store User')
