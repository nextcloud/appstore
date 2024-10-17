# Generated by Django 4.2.16 on 2024-10-17 08:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_donation'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppApiEnvironmentVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('env_name', models.CharField(max_length=64, verbose_name='Environment Variable Name')),
                ('display_name', models.CharField(max_length=128, verbose_name='Display Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('default', models.CharField(blank=True, max_length=256, verbose_name='Default Value')),
                ('app_release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='environment_variables', to='core.apprelease', verbose_name='App Release')),
            ],
            options={
                'verbose_name': 'AppAPI Release Environment Variable',
                'verbose_name_plural': 'AppAPI Release Environment Variables',
                'db_table': 'core_appapi_release_env_vars',
                'unique_together': {('app_release', 'env_name')},
            },
        ),
    ]
