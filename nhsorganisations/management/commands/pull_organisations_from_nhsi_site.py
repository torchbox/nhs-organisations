import os
import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Organisation, Region

_REGIONS_URL = os.getenv('NHSI_SITE_REGIONS_URL', 'https://improvement.nhs.uk/regions.json/')
_URL = os.getenv('NHSI_SITE_ORGS_URL', 'https://improvement.nhs.uk/organisations.json')

USER_AUTH_BASIC = os.getenv('NHSI_USER_AUTH_BASIC', '')
PASSWORD_AUTH_BASIC = os.getenv('NHSI_PASSWORD_AUTH_BASIC', '')
_AUTH_BASIC = (USER_AUTH_BASIC, PASSWORD_AUTH_BASIC) if USER_AUTH_BASIC else None

DCF_ORG_TYPES = [
    Organisation.TYPE_PROVIDER,
    Organisation.TYPE_INDEPENDENT_PROVIDER,
    Organisation.TYPE_COMMISSIONER,
    Organisation.TYPE_ALB,
    Organisation.TYPE_OTHER,
    Organisation.TYPE_PATHOLOGY_JV,
]

PP_ORG_TYPES = [
    Organisation.TYPE_PROVIDER,
    Organisation.TYPE_INDEPENDENT_PROVIDER,
    Organisation.TYPE_COMMISSIONER,
    Organisation.TYPE_ALB,
]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--dcf', action='store_true',
                            help='Only loads organisation types used by DCF')
        parser.add_argument('--pp', action='store_true',
                            help='Only loads organisation types used by Pricing Portal')

    help = (
        "Update local Organisations to reflect the data from {}. "
        "Organisations may change or close over time, but should never be "
        "deleted once created."
        .format(_URL)
    )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.only_orgs_for_dcf = kwargs['dcf']
        self.only_orgs_for_pp = kwargs['pp']

        if self.only_orgs_for_dcf and self.only_orgs_for_pp:
            print("You can only select only one flag, --dcf or --pp.")
            return

        print('----------------------------------------------------------')
        print('Refreshing region data')
        print('----------------------------------------------------------')
        self.refresh_region_data(**kwargs)

        print('----------------------------------------------------------')
        print('Refreshing organisation data')
        print('----------------------------------------------------------')
        self.refresh_organisation_data(**kwargs)

    def refresh_region_data(self, **kwargs):
        self.regions_by_id = {}

        print('Fetching region data...')
        try:
            response = requests.get(_REGIONS_URL, auth=_AUTH_BASIC)
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print("regions.json is not live yet, so skipping for now\n\n")
                self.regions_by_id = Region.objects.mapped_by_id()
                return
            raise e

        region_list = response.json()
        print('Updating region data...')
        for r in region_list:
            obj, created = Region.objects.update_or_create(
                id=r['id'],
                defaults=dict(
                    code=r['code'],
                    name=r['name'],
                    is_active=r['is_active']
                ),
            )
            self.regions_by_id[str(obj.id)] = obj
            if created:
                print("Added new region: %r" % obj)
            else:
                print("Updated existing region: %r" % obj)

        print('Setting region predecessor values...')
        for r in region_list:
            obj = self.regions_by_id[r['id']]
            predecessor_regions = [
                self.regions_by_id[pid] for pid in r['predecessor_ids']
                if pid in self.regions_by_id
            ]
            print('Setting predecessors for %r to:\n%r' % (obj, predecessor_regions))
            obj.predecessors.set(predecessor_regions)

        print('Done!\n\n')

    def refresh_organisation_data(self, **kwargs):
        print('Fetching organisation data...')
        response = requests.get(_URL, auth=_AUTH_BASIC)
        response.raise_for_status()

        existing_orgs = Organisation.objects.as_dict(keyed_by='code')
        successor_orgs_to_set = {}
        orgs_to_create = []

        print('Updating organisation data...')
        for org_code, org_details in response.json().items():
            if self.only_orgs_for_dcf:
                if org_details['organisation_type']['code'] not in DCF_ORG_TYPES:
                    continue

            if self.only_orgs_for_pp:
                if org_details['organisation_type']['code'] not in PP_ORG_TYPES:
                    continue

            org_details = self.prepare_organisation_data(org_details)
            print('----------------------------------------------------------')
            print("%s (%s)" % (org_details['name'], org_code))

            successor_code = org_details.pop('successor_org_code')
            if successor_code is not None:
                successor_orgs_to_set[org_code] = successor_code

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
        print('Done!\n\n')

    def prepare_organisation_data(self, org_details):
        try:
            successor_org_code = org_details['successor_organisation']['code']
        except (KeyError, TypeError):
            successor_org_code = None

        region_details = org_details.pop('region', None)
        if region_details:
            region = None
            if 'id' in region_details:
                region_id = region_details['id']
                region = self.regions_by_id.get(region_id)
            else:
                region_code = region_details['code']
                for r in self.regions_by_id.values():
                    if r.code == region_code:
                        region = r
                        break
            if region is None:
                raise ValueError(
                    "The region data for '{}' ({}) did not match up to a "
                    "region object. Please try running the command again."
                    .format(org_details['name'], org_details['code'])
                )
        else:
            region = None

        return {
            'name': org_details['name'],
            'organisation_type': org_details['organisation_type']['code'],
            'region': region,
            'closure_date': org_details['closure_date'],
            'created_at': org_details['created_at'],
            'last_updated_at': org_details['last_updated_at'],
            'successor_org_code': successor_org_code,
        }
