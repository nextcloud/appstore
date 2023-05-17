from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "nextcloudappstore.user"
    verbose_name = "App Store User"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready = False

    def ready(self):
        # during tests ready can be called more than once.
        if not self._ready:
            from . import signals  # noqa

            self._ready = True
