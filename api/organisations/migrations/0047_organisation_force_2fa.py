# Generated by Django 3.2.20 on 2023-10-23 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0046_allow_allowed_projects_to_be_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='force_2fa',
            field=models.BooleanField(default=False),
        ),
    ]
