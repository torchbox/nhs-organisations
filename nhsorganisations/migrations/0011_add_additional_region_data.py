# -*- coding: utf-8 -*-
from django.db import migrations


REGIONS = (
    # New regions
    dict(
        id='3c30900c-18f6-4122-971d-f0190f3e11a5',
        code="Y60",
        name="Midlands",
        predecessor_ids=["52a7f92a343e41f38ca22eb1d94d797b"],
    ),
    dict(
        id='e5ffa9cb-e123-4d7e-8c0d-8ab333ca154c',
        code="Y61",
        name="East of England",
        predecessor_ids=["52a7f92a343e41f38ca22eb1d94d797b"],
    ),
    dict(
        id='adac8ebf-44c2-44c0-830f-d3bfe83df699',
        code="Y62",
        name="North West",
        predecessor_ids=["ff5ce1d32d77497bb9e967c1d56f8dd9"],
    ),
    dict(
        id='ff30de4d-4f25-4a7d-82d9-43580aab3122',
        code="Y63",
        name="North East and Yorkshire",
        predecessor_ids=["ff5ce1d32d77497bb9e967c1d56f8dd9"],
    ),
)


def migrate_forwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")
    regions_by_pk = {}
    for details in REGIONS:
        predecessor_ids = details.pop('predecessor_ids', [])
        obj = Region.objects.create(**details)
        regions_by_pk[obj.pk] = obj
        print('debug')
        for pid in predecessor_ids:
            print("pid")
            print(pid)
            obj.predecessors.add(regions_by_pk[pid])


def migrate_backwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")
    Region.objects.filter(id__in=set(r['id'] for r in REGIONS)).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('nhsorganisations', '0010_update_Y59_region_code'),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
