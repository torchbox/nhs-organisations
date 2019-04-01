# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_forwards(apps, schema_editor):
    Region = apps.get_model("organisations", "Region")

    south_west_region = Region.objects.get(code="Y57")
    south_west_region.code = "Y59"
    south_west_region.save()


def migrate_backwards(apps, schema_editor):
    Region = apps.get_model("organisations", "Region")

    south_west_region = Region.objects.get(code="Y59")
    south_west_region.code = "Y57"
    south_west_region.save()


class Migration(migrations.Migration):
    dependencies = [
        ('organisations', '0009_rename_region_new_to_region'),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
