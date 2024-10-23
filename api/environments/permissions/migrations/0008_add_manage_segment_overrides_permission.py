# Generated by Django 3.2.20 on 2023-11-01 19:54

from common.environments.permissions import (
    MANAGE_SEGMENT_OVERRIDES,
    UPDATE_FEATURE_STATE,
)
from core.migration_helpers import create_new_environment_permissions
from django.db import migrations

from permissions.models import ENVIRONMENT_PERMISSION_TYPE


def add_manage_segment_overrides_permission(apps, schema_editor):
    PermissionModel = apps.get_model("permissions", "PermissionModel")
    UserEnvironmentPermission = apps.get_model(
        "environment_permissions",
        "UserEnvironmentPermission",
    )
    UserPermissionGroupEnvironmentPermission = apps.get_model(
        "environment_permissions",
        "UserPermissionGroupEnvironmentPermission",
    )
    manage_segment_overrides_permission, _ = PermissionModel.objects.get_or_create(
        key=MANAGE_SEGMENT_OVERRIDES,
        description="Permission to manage segment overrides in the given environment",
        type=ENVIRONMENT_PERMISSION_TYPE,
    )

    # Add MANAGE_SEGMENT_OVERRIDES to existing UPDATE_FEATURE_STATE holders
    create_new_environment_permissions(
        UPDATE_FEATURE_STATE,
        UserEnvironmentPermission,
        "userenvironmentpermission",
        [manage_segment_overrides_permission],
    )
    create_new_environment_permissions(
        UPDATE_FEATURE_STATE,
        UserPermissionGroupEnvironmentPermission,
        "userpermissiongroupenvironmentpermission",
        [manage_segment_overrides_permission],
    )


def remove_manage_segment_overrides_permission(apps, schema_editor):
    PermissionModel = apps.get_model("permissions", "PermissionModel")
    PermissionModel.objects.filter(key=MANAGE_SEGMENT_OVERRIDES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("environment_permissions", "0007_add_unique_permission_constraint"),
    ]

    operations = [
        migrations.RunPython(
            add_manage_segment_overrides_permission,
            reverse_code=remove_manage_segment_overrides_permission,
        )
    ]
