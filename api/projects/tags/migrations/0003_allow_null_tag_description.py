# Generated by Django 3.2.13 on 2022-06-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_auto_20210223_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
