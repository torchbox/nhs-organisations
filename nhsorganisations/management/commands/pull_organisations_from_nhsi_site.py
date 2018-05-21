import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Organisation

_URL = 'https://improvement.nhs.uk/organisations.json'


def simplify_api_organisation_dict(org_details):
    try:
        region = org_details['region']['code']
    except (KeyError, TypeError):
        region = ''

    try:
        successor_org_code = org_details['successor_organisation']['code']
    except (KeyError, TypeError):
        successor_org_code = None

    return {
        'name': org_details['name'],
        'organisation_type': org_details['organisation_type']['code'],
        'region': region,
        'closure_date': org_details['closure_date'],
        'created_at': org_details['created_at'],
        'last_updated_at': org_details['last_updated_at'],
        'successor_org_code': successor_org_code,
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
        existing_orgs_dict = Organisation.objects.as_dict(keyed_by='code')
        orgs_to_create = []
        successor_orgs_to_set = {}
        print('Processing data...')
        for org_code, org_details in result.items():
            org_details = simplify_api_organisation_dict(org_details)
            print('----------------------------------------------------------')
            print("%s (%s)" % (org_details['name'], org_code))

            successor_code = org_details.pop('successor_org_code')
            if successor_code is not None:
                successor_orgs_to_set[org_code] = successor_code

            if org_code in existing_orgs_dict:
                print("Updating local copy")
                obj = existing_orgs_dict[org_code]
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
        if successor_orgs_to_set:
            print('----------------------------------------------------------')
            print("Setting successor organisations for merged orgs...")
            successor_org_codes = successor_orgs_to_set.values()
            succeeded_org_codes = successor_orgs_to_set.keys()
            successor_orgs_dict = Organisation.objects.filter(code__in=successor_org_codes).as_dict(keyed_by='code')
            for org in Organisation.objects.filter(code__in=succeeded_org_codes):
                successor_code = successor_orgs_to_set[org.code]
                successor_org = successor_orgs_dict.get(successor_code)
                if successor_org:
                    org.successor_id = successor_org.id
                    org.save()
        print('----------------------------------------------------------')
        print('Done!')
