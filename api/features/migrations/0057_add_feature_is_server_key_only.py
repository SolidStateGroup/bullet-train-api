# Generated by Django 3.2.18 on 2023-05-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("features", "0056_alter_featurestate_change_request"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="is_server_key_only",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicalfeature",
            name="is_server_key_only",
            field=models.BooleanField(default=False),
        ),
    ]
