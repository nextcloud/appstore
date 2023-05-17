from django import template

from nextcloudappstore.core.models import App, AppRelease

register = template.Library()


@register.filter(name="compatible_releases")
def compatible_releases(app: App, version: str) -> AppRelease:
    return app.compatible_releases(version)
