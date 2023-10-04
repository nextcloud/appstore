# Generated by Django 1.9.8 on 2016-09-13 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apprelease',
            name='min_int_size',
            field=models.IntegerField(blank=True, default=32, help_text='e.g. 32 for 32-bit Integers', verbose_name='Minimum Integer bits'),
        ),
    ]
