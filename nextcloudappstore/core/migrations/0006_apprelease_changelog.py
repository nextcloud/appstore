# Generated by Django 1.10.2 on 2016-10-02 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_app_ocsid'),
    ]

    operations = [
        migrations.AddField(
            model_name='apprelease',
            name='changelog',
            field=models.TextField(default='', help_text='The release changelog. Can contain Markdown', verbose_name='Changelog'),
        ),
    ]
