# Generated by Django 3.2.25 on 2024-06-11 11:17

from django.db import migrations, models
import django.db.models.deletion
import django_lifecycle.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('environments', '0034_alter_environment_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrafanaConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('base_url', models.URLField(null=True)),
                ('api_key', models.CharField(max_length=100)),
                ('environment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='grafana_config', to='environments.environment')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
    ]
