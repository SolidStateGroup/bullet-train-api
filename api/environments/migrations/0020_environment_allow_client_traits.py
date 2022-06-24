# Generated by Django 3.2.13 on 2022-06-24 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('environments', '0019_allow_blank_minimum_change_request_approvals'),
    ]

    operations = [
        migrations.AddField(
            model_name='environment',
            name='allow_client_traits',
            field=models.BooleanField(default=True, help_text='Allows clients using the client API key to set traits.'),
        ),
    ]
