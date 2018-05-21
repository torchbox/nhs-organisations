from django.test import TestCase

from nhsorganisations.utils.testing import create_minimal_organisations
from nhsorganisations.models import Organisation


class TestCreateMinimalOrganisations(TestCase):

    def test_creates_expected_number_of_orgs(self):
        create_minimal_organisations()
        self.assertEqual(Organisation.objects.count(), 14)
