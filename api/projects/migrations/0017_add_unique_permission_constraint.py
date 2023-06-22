# Generated by Django 3.2.18 on 2023-06-22 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_soft_delete_projects'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='userpermissiongroupprojectpermission',
            constraint=models.UniqueConstraint(fields=('group', 'project'), name='unique_group_project_permission'),
        ),
        migrations.AddConstraint(
            model_name='userprojectpermission',
            constraint=models.UniqueConstraint(fields=('user', 'project'), name='unique_user_project_permission'),
        ),
    ]
