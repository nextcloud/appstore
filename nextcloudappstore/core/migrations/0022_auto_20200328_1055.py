import django.db.models.deletion
import parler.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_nextcloudrelease_is_supported'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='is_integration',
            field=models.BooleanField(default=False, verbose_name='Integration (i.e. Outlook plugin)'),
        ),
        migrations.AlterField(
            model_name='appratingtranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.AppRating'),
        ),
        migrations.AlterField(
            model_name='appreleasetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.AppRelease'),
        ),
        migrations.AlterField(
            model_name='apptranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.App'),
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.Category'),
        ),
    ]
