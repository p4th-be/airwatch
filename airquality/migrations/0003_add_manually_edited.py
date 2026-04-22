from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airquality', '0002_add_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollutant',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='country',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='city',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='measurementstation',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='airqualitydata',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='healthimpact',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
        migrations.AddField(
            model_name='datasource',
            name='manually_edited',
            field=models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques"),
        ),
    ]
