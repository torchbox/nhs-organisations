from django.utils import timezone
from ..models import Organisation, Region


def get_common_region_ids():
    return {
        'NORTH': 'ff5ce1d3-2d77-497b-b9e9-67c1d56f8dd9',
        'MIDLANDS_AND_EAST': '52a7f92a-343e-41f3-8ca2-2eb1d94d797b',
        'LONDON': '358dab2d-c8ed-4a6a-91a0-e41d57a2f008',
        'SOUTH_EAST': 'aa8e1862-6071-4a67-857c-9bf1601d4ef4',
        'SOUTH_WEST': 'ab827d39-7da9-4aba-aa64-dc4aefc94b37',
        'WALES': '179a0109-469d-4d7c-a67d-e3cc0052ba93',
    }


def get_common_regions():
    regions = Region.objects.mapped_by_id()
    return {
        label: regions[region_id]
        for label, region_id in get_common_region_ids().items()
    }


def create_minimal_organisations(create_for_each_region=False):
    regions = get_common_regions()

    org_details = (
        # --------------------------------------------------------------------
        # Some important ones
        # --------------------------------------------------------------------
        dict(
            id=1,
            code='Z01',
            name="NHS Improvement",
            organisation_type=Organisation.TYPE_ALB,
        ),
        dict(
            id=2,
            code='Z45',
            name="NHS England",
            organisation_type=Organisation.TYPE_OTHER,
        ),
        # --------------------------------------------------------------------
        # A provider for each region
        # --------------------------------------------------------------------
        dict(
            id=3,
            code='RMC',
            name="Bolton NHS Foundation Trust",
            region=regions['NORTH'],
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=4,
            code='RGQ',
            name="Ipswich Hospital NHS Trust",
            region=regions['MIDLANDS_AND_EAST'],
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=5,
            code='R1H',
            name="Barts Health NHS Trust",
            region=regions['LONDON'],
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=6,
            code='RXQ',
            name="Buckinghamshire Healthcare NHS Trust",
            region=regions['SOUTH_EAST'],
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=7,
            code='RK9',
            name="Plymouth Hospitals NHS Trust",
            region=regions['SOUTH_WEST'],
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        # --------------------------------------------------------------------
        # A closed provider
        # --------------------------------------------------------------------
        dict(
            id=8,
            code='RVN',
            name="Avon and Wiltshire Mental Health Partnership NHS Trust",
            region=regions['SOUTH_WEST'],
            organisation_type=Organisation.TYPE_PROVIDER,
            closure_date=timezone.now(),
        ),
        # --------------------------------------------------------------------
        # Some merged CCGs
        # --------------------------------------------------------------------
        dict(
            id=9,
            code='15E',
            name="NHS Birmingham and Solihull CCG",
            region=regions['MIDLANDS_AND_EAST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        dict(
            id=10,
            code='13P',
            name="NHS Birmingham CrossCity CCG",
            region=regions['MIDLANDS_AND_EAST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        dict(
            id=11,
            code='04X',
            name="NHS Birmingham South and Central CCG",
            region=regions['MIDLANDS_AND_EAST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        dict(
            id=12,
            code='05P',
            name="NHS Solihull CCG",
            region=regions['MIDLANDS_AND_EAST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        # --------------------------------------------------------------------
        # And CCGs for other regions
        # --------------------------------------------------------------------
        dict(
            id=13,
            code='03F',
            name="NHS Hull CCG",
            region=regions['NORTH'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        dict(
            id=14,
            code='08A',
            name="NHS Greenwich CCG",
            region=regions['LONDON'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        dict(
            id=15,
            code='10Q',
            name="NHS Oxfordshire CCG",
            region=regions['SOUTH_EAST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        dict(
            id=16,
            code='15C',
            name="NHS Bristol, North Somerset and South Gloucestershire CCG",
            region=regions['SOUTH_WEST'],
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        # --------------------------------------------------------------------
        # A couple of independent providers
        # --------------------------------------------------------------------
        dict(
            id=17,
            code='NTG',
            name="Marie Stopes International",
            organisation_type=Organisation.TYPE_INDEPENDENT_PROVIDER,
        ),
        dict(
            id=18,
            code='NKI',
            name="Turning Point",
            organisation_type=Organisation.TYPE_INDEPENDENT_PROVIDER,
        ),
    )

    now = timezone.now()
    Organisation.objects.bulk_create(
        Organisation(created_at=now, last_updated_at=now, **details)
        for details in org_details
    )
