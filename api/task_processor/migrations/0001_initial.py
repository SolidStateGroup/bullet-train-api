# Generated by Django 3.2.14 on 2022-07-08 14:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('scheduled_for', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('pickled_callable', models.BinaryField()),
                ('pickled_args', models.BinaryField(blank=True, null=True)),
                ('pickled_kwargs', models.BinaryField(blank=True, null=True)),
            ],
        ),
    ]
