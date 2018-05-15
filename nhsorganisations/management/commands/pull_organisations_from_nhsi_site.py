import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Organisation

_URL = 'https://improvement.nhs.uk/organisations.json'


def simplify_api_organisation_dict(org_details):
    try:
        region = org_details['region']['code']
    except TypeError:
        region = ''

    return {
        'name': org_details['name'],
        'organisation_type': org_details['organisation_type']['code'],
        'region': region,
        'closure_date': org_details['closure_date'],
        'created_at': org_details['created_at'],
        'last_updated_at': org_details['last_updated_at'],
    }


class Command(BaseCommand):
    help = (
        "Update local Organisations to reflect the data from {}. "
        "Organisations may change or close over time, but should never be "
        "deleted once created."
        .format(_URL)
    )

    @transaction.atomic
    def handle(self, **kwargs):
        print('Fetching data...')
        result = requests.get(_URL).json()
        existing_orgs = Organisation.objects.as_dict(keyed_by='code')
        orgs_to_create = []
        print('Processing data...')
        for org_code, org_details in result.items():
            org_details = simplify_api_organisation_dict(org_details)
            print('----------------------------------------------------------')
            print("%s (%s)" % (org_details['name'], org_code))
            if org_code in existing_orgs:
                print("Updating local copy")
                obj = existing_orgs[org_code]
                for key, val in org_details.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                print("Creating a local copy")
                org_details['code'] = org_code
                orgs_to_create.append(Organisation(**org_details))
        if orgs_to_create:
            print('----------------------------------------------------------')
            print("Saving %s new organisations..." % len(orgs_to_create))
            Organisation.objects.bulk_create(orgs_to_create)
        print('----------------------------------------------------------')
        print('Done!')
