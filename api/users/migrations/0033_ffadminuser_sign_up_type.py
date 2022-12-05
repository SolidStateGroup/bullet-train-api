# Generated by Django 3.2.16 on 2022-11-08 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_auto_20221107_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='ffadminuser',
            name='sign_up_type',
            field=models.CharField(blank=True, choices=[('NO_INVITE', 'No Invite'), ('INVITE_EMAIL', 'Invite Email'), ('INVITE_LINK', 'Invite Link')], max_length=100, null=True),
        ),
    ]
