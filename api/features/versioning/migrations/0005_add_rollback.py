# Generated by Django 3.2.25 on 2024-08-07 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_versioning', '0004_add_version_change_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='environmentfeatureversion',
            name='rolled_back_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalenvironmentfeatureversion',
            name='rolled_back_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]