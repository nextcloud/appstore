# Generated by Django 1.10.6 on 2017-03-25 20:09
#
#SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
#SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20161128_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appownershiptransfer',
            name='app',
        ),
        migrations.RemoveField(
            model_name='appownershiptransfer',
            name='from_user',
        ),
        migrations.RemoveField(
            model_name='appownershiptransfer',
            name='to_user',
        ),
        migrations.AddField(
            model_name='app',
            name='ownership_transfer_enabled',
            field=models.BooleanField(default=False, help_text='If enabled, a user can try to register the same app again using the public certificate and signature. If he does, the app will be transferred to him.', verbose_name='Ownership transfer enabled'),
        ),
        migrations.DeleteModel(
            name='AppOwnershipTransfer',
        ),
    ]
