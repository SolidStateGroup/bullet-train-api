# Generated by Django 3.2.23 on 2023-12-14 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('segments', '0019_add_audit_to_condition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalcondition',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical condition', 'verbose_name_plural': 'historical conditions'},
        ),
        migrations.AlterModelOptions(
            name='historicalsegment',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical segment', 'verbose_name_plural': 'historical segments'},
        ),
        migrations.AddField(
            model_name='historicalcondition',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalsegment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalcondition',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalsegment',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
