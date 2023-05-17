from typing import Any

from django.apps import AppConfig


class CertificateConfig(AppConfig):
    name = "nextcloudappstore.certificate"
    verbose_name = "App Store Certificate"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._ready = False

    def ready(self) -> None:
        # during tests ready can be called more than once.
        if not self._ready:
            self._ready = True
