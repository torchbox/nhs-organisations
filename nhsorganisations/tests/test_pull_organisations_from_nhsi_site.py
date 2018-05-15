from django.core.management import call_command
from django.test import TestCase

from nhsorganisations.models import Organisation


class TestPullOrganisationsWhenPopulated(TestCase):

    fixtures = ['organisations.json']

    def test_no_orgs_are_deleted(self):
        # Fetch current pks and confirm there are a decent number of orgs
        existing_org_ids = set(
            Organisation.objects.all().values_list('pk', flat=True)
        )
        self.assertGreater(len(existing_org_ids), 200)
        # Run the command
        call_command('pull_organisations_from_nhsi_site')
        new_org_ids = set(
            Organisation.objects.all().values_list('pk', flat=True)
        )
        # The number of orgs should never be less after running
        self.assertGreaterEqual(len(new_org_ids), len(existing_org_ids))
        # Confirm that all of the pks we had orginally still exist
        for org_id in existing_org_ids:
            self.assertIn(org_id, new_org_ids)
