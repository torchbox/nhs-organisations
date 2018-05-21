from django.utils import timezone
from ..models import Organisation


def create_minimal_organisations(create_for_each_region=False):
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
            region=Organisation.REGION_NORTH_ENGLAND,
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=4,
            code='RGQ',
            name="Ipswich Hospital NHS Trust",
            region=Organisation.REGION_MIDLANDS_AND_EAST_ENGLAND,
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=5,
            code='R1H',
            name="Barts Health NHS Trust",
            region=Organisation.REGION_LONDON,
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=6,
            code='RXQ',
            name="Buckinghamshire Healthcare NHS Trust",
            region=Organisation.REGION_SOUTH_EAST,
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        dict(
            id=7,
            code='RK9',
            name="Plymouth Hospitals NHS Trust",
            region=Organisation.REGION_SOUTH_WEST,
            organisation_type=Organisation.TYPE_PROVIDER,
        ),
        # --------------------------------------------------------------------
        # A closed provider
        # --------------------------------------------------------------------
        dict(
            id=8,
            code='RVN',
            name="Avon and Wiltshire Mental Health Partnership NHS Trust",
            region=Organisation.REGION_SOUTH_WEST,
            organisation_type=Organisation.TYPE_PROVIDER,
            closure_date=timezone.now(),
        ),
        # --------------------------------------------------------------------
        # Some merged CCGs
        # --------------------------------------------------------------------
        dict(
            id=9,
            code='578',
            name="NHS Birmingham and Solihull CCG",
            region=Organisation.REGION_MIDLANDS_AND_EAST_ENGLAND,
            organisation_type=Organisation.TYPE_COMMISSIONER,
        ),
        dict(
            id=10,
            code='13P',
            name="NHS Birmingham CrossCity CCG",
            region=Organisation.REGION_MIDLANDS_AND_EAST_ENGLAND,
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        dict(
            id=11,
            code='04X',
            name="NHS Birmingham South and Central CCG",
            region=Organisation.REGION_MIDLANDS_AND_EAST_ENGLAND,
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        dict(
            id=12,
            code='05P',
            name="NHS Solihull CCG",
            region=Organisation.REGION_MIDLANDS_AND_EAST_ENGLAND,
            organisation_type=Organisation.TYPE_COMMISSIONER,
            closure_date=timezone.now(),
            successor_id=9,
        ),
        # --------------------------------------------------------------------
        # A couple of independent providers
        # --------------------------------------------------------------------
        dict(
            id=13,
            code='NTG',
            name="Marie Stopes International",
            organisation_type=Organisation.TYPE_INDEPENDENT_PROVIDER,
        ),
        dict(
            id=14,
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
