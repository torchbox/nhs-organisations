# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_forwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")

    try:
        south_west_region = Region.objects.get(code="Y57")
        south_west_region.code = "Y59"
        south_west_region.save()
    except Region.DoesNotExist:
        pass

def migrate_backwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")

    try:
        south_west_region = Region.objects.get(code="Y59")
        south_west_region.code = "Y57"
        south_west_region.save()
    except Region.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ('nhsorganisations', '0009_rename_region_new_to_region'),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
