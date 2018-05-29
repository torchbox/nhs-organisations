from collections import defaultdict

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .query import OrganisationQuerySet


class Organisation(models.Model):
    """An organisation operating as part of, or in partnership with, the NHS"""

    TYPE_PROVIDER = 'provider'
    TYPE_INDEPENDENT_PROVIDER = 'independent-provider'
    TYPE_COMMISSIONER = 'commissioner'
    TYPE_ALB = 'alb'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = (
        (TYPE_PROVIDER, _('Provider')),
        (TYPE_COMMISSIONER, _('Commissioner')),
        (TYPE_ALB, _("Arm's Length Body (ALB)")),
        (TYPE_INDEPENDENT_PROVIDER, _('Independent Provider')),
        (TYPE_OTHER, _('Other')),
    )
    TYPE_CHOICES_PLURALISED = (
        (TYPE_PROVIDER, _('Providers')),
        (TYPE_COMMISSIONER, _('Commissioners')),
        (TYPE_ALB, _("Arm's Length Bodies")),
        (TYPE_INDEPENDENT_PROVIDER, _('Independent Providers')),
        (TYPE_OTHER, _('Other')),
    )

    REGION_NORTH_ENGLAND = 'Y54'
    REGION_MIDLANDS_AND_EAST_ENGLAND = 'Y55'
    REGION_LONDON = 'Y56'
    REGION_SOUTH_EAST = 'Y57'
    REGION_SOUTH_WEST = 'Y58'
    REGIONS = (
        REGION_NORTH_ENGLAND,
        REGION_MIDLANDS_AND_EAST_ENGLAND,
        REGION_LONDON,
        REGION_SOUTH_EAST,
        REGION_SOUTH_WEST,
    )
    REGION_CHOICES_NO_BLANK = (
        (REGION_NORTH_ENGLAND, _('North of England')),
        (REGION_MIDLANDS_AND_EAST_ENGLAND, _('Midlands and East of England')),
        (REGION_LONDON, _('London')),
        (REGION_SOUTH_EAST, _('South East')),
        (REGION_SOUTH_WEST, _('South West')),
    )
    REGION_CHOICES = (('', _('None')),) + REGION_CHOICES_NO_BLANK
    REGION_CHOICES_OPTGROUPS = (('', _('Non-Regional')),) + REGION_CHOICES_NO_BLANK

    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    organisation_type = models.CharField(
        verbose_name=_('organisation type'),
        db_index=True,
        max_length=25,
        choices=TYPE_CHOICES,
        default=TYPE_OTHER,
    )
    region = models.CharField(
        db_index=True,
        max_length=3,
        blank=True,
        choices=REGION_CHOICES,
    )
    closure_date = models.DateTimeField(null=True, blank=True)
    successor = models.ForeignKey(
        'self',
        related_name='predecessors',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(editable=False)
    last_updated_at = models.DateTimeField(editable=False)

    objects = OrganisationQuerySet.as_manager()

    class Meta:
        verbose_name = _('organisation')
        verbose_name_plural = _('organisations')
        ordering = ('name',)

    def __str__(self):
        return '{name} ({code})'.format(name=self.name, code=self.code)

    def get_merge_history(
        self, include_successor=True, group_by_date=True, for_date=None,
        include_predecessor_history=False
    ):
        if include_successor and self.successor:
            yield {
                'date': self.closure_date.strftime('%Y-%m-%d'),
                'successor_org': self.successor,
                'predecessor_org': self,
            }

        qs = self.predecessors.all()
        if include_predecessor_history:
            qs = qs.prefetch_related('predecessors')
        if for_date:
            qs = qs.filter(closure_date=for_date)
        predecessors = tuple(qs.order_by('-closure_date'))

        if not group_by_date:
            for org in predecessors:
                yield {
                    'date': org.closure_date.strftime('%Y-%m-%d'),
                    'successor_org': self,
                    'predecessor_org': org,
                }
        else:
            predecessors_by_date = defaultdict(list)
            for org in predecessors:
                key = org.closure_date.strftime('%Y-%m-%d')
                predecessors_by_date[key].append(org)
            for merge_date, orgs in predecessors_by_date.items():
                yield {
                    'date': merge_date,
                    'successor_org': self,
                    'predecessor_orgs': orgs,
                }

        if include_predecessor_history:
            for org in predecessors:
                for item in org.get_merge_history(
                    include_successor=False,
                    include_predecessor_history=True,
                    group_by_date=group_by_date,
                ):
                    yield item
