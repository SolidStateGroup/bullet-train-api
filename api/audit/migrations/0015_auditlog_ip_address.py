# Generated by Django 3.2.23 on 2023-12-14 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0014_auditlog__organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
