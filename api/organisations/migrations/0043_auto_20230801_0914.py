# Generated by Django 3.2.20 on 2023-08-01 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0042_alter_subscription_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisationwebhook',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='organisationwebhook',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
