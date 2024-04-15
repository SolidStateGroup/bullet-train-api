# Generated by Django 3.2.23 on 2023-12-14 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0049_subscription_billing_status'),
        ('audit', '0013_allow_manual_override_of_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='_organisation',
            field=models.ForeignKey(db_column='organisation', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='organisations.organisation'),
        ),
    ]
