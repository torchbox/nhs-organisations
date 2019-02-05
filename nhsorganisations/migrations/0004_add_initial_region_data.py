# -*- coding: utf-8 -*-
from django.db import migrations


REGIONS = (
    # Original regions
    dict(
        id='ff5ce1d3-2d77-497b-b9e9-67c1d56f8dd9',
        code="Y54",
        name="North of England",
    ),
    dict(
        id='52a7f92a-343e-41f3-8ca2-2eb1d94d797b',
        code="Y55",
        name="Midlands and East of England",
    ),
    dict(
        id='358dab2d-c8ed-4a6a-91a0-e41d57a2f008',
        code="Y56",
        name="London",
    ),
    dict(
        id='10e2d83d-adf3-4b5e-9706-5e9e2d53f3c1',
        code="SOUTH",  # Will be corrected to Y57 at a later time
        name="South",
        is_active=False,
    ),
    dict(
        id='aa8e1862-6071-4a67-857c-9bf1601d4ef4',
        code="Y57",  # Will be corrected to Y59 at a later time
        name="South East",
        predecessor_ids=["10e2d83d-adf3-4b5e-9706-5e9e2d53f3c1"],
    ),
    dict(
        id='ab827d39-7da9-4aba-aa64-dc4aefc94b37',
        code="Y58",
        name="South West",
        predecessor_ids=["10e2d83d-adf3-4b5e-9706-5e9e2d53f3c1"],
    ),
    dict(
        id='179a0109-469d-4d7c-a67d-e3cc0052ba93',
        code="W00",
        name="Wales",
    ),
)


def migrate_forwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")
    regions_by_pk = {}
    for details in REGIONS:
        predecessor_ids = details.pop('predecessor_ids', [])
        obj = Region.objects.create(**details)
        regions_by_pk[obj.pk] = obj
        for pid in predecessor_ids:
            obj.predecessors.add(regions_by_pk[pid])


def migrate_backwards(apps, schema_editor):
    Region = apps.get_model("nhsorganisations", "Region")
    Region.objects.filter(id__in=set(r['id'] for r in REGIONS)).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('nhsorganisations', '0003_add_region_model'),
    ]

    operations = [
        migrations.RunPython(migrate_forwards, migrate_backwards),
    ]
