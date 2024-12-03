# Generated by Django 2.2.10 on 2020-02-20 00:24

from common.environments.permissions import (
    APPROVE_CHANGE_REQUEST,
    CREATE_CHANGE_REQUEST,
    MANAGE_IDENTITIES,
    UPDATE_FEATURE_STATE,
    VIEW_ENVIRONMENT,
)
from common.projects.permissions import PROJECT_PERMISSIONS
from django.db import migrations, models

from permissions.models import (
    ENVIRONMENT_PERMISSION_TYPE,
    PROJECT_PERMISSION_TYPE,
)

ENVIRONMENT_PERMISSIONS = [
    (VIEW_ENVIRONMENT, "View permission for the given environment."),
    (UPDATE_FEATURE_STATE, "Update the state or value for a given feature state."),
    (MANAGE_IDENTITIES, "Manage identities in the given environment."),
    (
        CREATE_CHANGE_REQUEST,
        "Permission to create change requests in the given environment.",
    ),
    (
        APPROVE_CHANGE_REQUEST,
        "Permission to approve change requests in the given environment.",
    ),
]


def insert_default_project_permissions(apps, schema_model):
    PermissionModel = apps.get_model("permissions", "PermissionModel")

    project_permissions = []
    for permission in PROJECT_PERMISSIONS:
        project_permissions.append(
            PermissionModel(
                key=permission[0],
                description=permission[1],
                type=PROJECT_PERMISSION_TYPE,
            )
        )

    PermissionModel.objects.bulk_create(project_permissions)


def insert_default_environment_permissions(apps, schema_model):
    PermissionModel = apps.get_model("permissions", "PermissionModel")

    environment_permissions = []
    for permission in ENVIRONMENT_PERMISSIONS:
        environment_permissions.append(
            PermissionModel(
                key=permission[0],
                description=permission[1],
                type=ENVIRONMENT_PERMISSION_TYPE,
            )
        )

    PermissionModel.objects.bulk_create(environment_permissions)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PermissionModel",
            fields=[
                (
                    "key",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("description", models.TextField()),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("PROJECT", "Project"),
                            ("ENVIRONMENT", "Environment"),
                        ],
                        max_length=100,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            insert_default_project_permissions, reverse_code=lambda *args: None
        ),
        migrations.RunPython(
            insert_default_environment_permissions, reverse_code=lambda *args: None
        ),
    ]
