# Generated by Django 3.2.18 on 2023-06-26 12:15

from django.db import migrations

from util.migrations import merge_duplicate_permissions


def merge_duplicate_organisation_permissions(apps, schema_editor):
    UserOrganisationPermission = apps.get_model(
        "organisation_permissions", "UserOrganisationPermission"
    )
    UserPermissionGroupOrganisationPermission = apps.get_model(
        "organisation_permissions", "UserPermissionGroupOrganisationPermission"
    )
    merge_duplicate_permissions(UserOrganisationPermission, ["user", "organisation"])
    merge_duplicate_permissions(
        UserPermissionGroupOrganisationPermission, ["group", "organisation"]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("organisation_permissions", "0002_add_related_query_name"),
    ]

    operations = [
        migrations.RunPython(
            merge_duplicate_organisation_permissions,
            reverse_code=migrations.RunPython.noop,
        )
    ]
