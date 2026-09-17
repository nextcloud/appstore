#SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
#SPDX-License-Identifier: AGPL-3.0-or-later

from base64 import urlsafe_b64encode

from django.db import migrations, models


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
        # Widen the column BEFORE rewriting the values. Proxying replaces the URL with
        # USERCONTENT_PROXY_URL + '/' + urlsafe_b64encode(url), and base64 costs 4 bytes per 3,
        # so a source URL longer than 162 characters no longer fits varchar(256) and the data
        # migration below fails with "value too long for type character varying(256)".
        # info.xsd caps a screenshot URL at 256 characters, so the widest possible result is
        # 39 + 4 * ceil(256 / 3) = 383; 512 covers that with room to spare.
        # On PostgreSQL, increasing a varchar length is a catalogue-only change, so this is
        # effectively instant and does not rewrite the table.
        migrations.AlterField(
            model_name='screenshot',
            name='url',
            field=models.URLField(max_length=512, verbose_name='Image URL'),
        ),
        migrations.RunPython(
            convert_screenshot_urls_to_usercontent,
            migrations.RunPython.noop,
        ),
    ]
