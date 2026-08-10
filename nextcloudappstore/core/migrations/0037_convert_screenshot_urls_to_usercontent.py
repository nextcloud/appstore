#SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
#SPDX-License-Identifier: AGPL-3.0-or-later

from base64 import urlsafe_b64encode

from django.db import migrations


def convert_screenshot_urls_to_usercontent(apps, schema_editor):
    from django.conf import settings

    Screenshot = apps.get_model('core', 'Screenshot')
    base = settings.USERCONTENT_PROXY_URL
    for screenshot in Screenshot.objects.all():
        url = screenshot.url
        if not url or url.startswith(base):
            continue
        base64_url = urlsafe_b64encode(url.encode()).decode()
        screenshot.url = f"{base}/{base64_url}"
        screenshot.save(update_fields=['url'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_app_is_enterprise_only'),
    ]

    operations = [
        migrations.RunPython(
            convert_screenshot_urls_to_usercontent,
            migrations.RunPython.noop,
        ),
    ]
