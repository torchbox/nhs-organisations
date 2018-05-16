from django.core.management import call_command
from django.test import TestCase

from nhsorganisations.models import Organisation


class TestPullOrganisationsWhenPopulated(TestCase):

    def test_no_orgs_are_deleted(self):
        self.assertEqual(Organisation.objects.all().count(), 0)

        # Run the command to populate from scratch
        call_command('pull_organisations_from_nhsi_site')
        org_ids = list(Organisation.objects.all().values_list('id', flat=True))
        self.assertGreater(len(org_ids), 0)

        # Run the command again to update
        call_command('pull_organisations_from_nhsi_site')
        new_org_ids = list(Organisation.objects.all().values_list('id', flat=True))

        # Confirm that all of the ids that existed before still exist
        for id in org_ids:
            self.assertIn(id, new_org_ids)
