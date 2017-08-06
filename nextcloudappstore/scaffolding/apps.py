from django.apps import AppConfig


class ScaffoldingConfig(AppConfig):
    name = 'nextcloudappstore.scaffolding'
    verbose_name = 'App Store Scaffolding'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready = False

    def ready(self):
        # during tests ready can be called more than once.
        if not self._ready:
            self._ready = True
