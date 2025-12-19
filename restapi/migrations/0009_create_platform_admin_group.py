from django.db import migrations


def create_platform_admin_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Platform Admin')


def remove_platform_admin_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Platform Admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0008_mentor_user'),
    ]

    operations = [
        migrations.RunPython(create_platform_admin_group, remove_platform_admin_group),
    ]
