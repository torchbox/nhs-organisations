from uuid import UUID
from collections import defaultdict

from django.db.models import Case, IntegerField, Q, QuerySet, When
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class RegionQuerySet(QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def in_use(self):
        from .models import Organisation
        return self.filter(id__in=Organisation.objects.values_list('region_new_id', flat=True))

    def mapped_by_id(self):
        return {str(obj.id): obj for obj in self.all()}

    def as_choices(self, add_blank_choice=False, blank_choice_label='---'):
        result = list(self.values_list('id', 'name'))
        if add_blank_choice:
            result.insert(0, (None, blank_choice_label))
        return result


class OrganisationQuerySet(QuerySet):

    def open_q(self, until_datetime):
        return Q(closure_date__isnull=True) | Q(closure_date__gt=until_datetime)

    def open(self):
        return self.filter(self.open_q(until_datetime=timezone.now()))

    def closed(self):
        return self.exclude(self.open_q(until_datetime=timezone.now()))

    def merged(self):
        return self.closed().filter(successor_id__isnull=False)

    def annotate_with_is_closed(self):
        return self.annotate(is_closed=Case(
            When(closure_date__isnull=True, then=0),
            When(closure_date__gt=timezone.now(), then=0),
            default=1,
            output_field=IntegerField()
        ))

    def of_type_q(self, organisation_type):
        valid_type_vals = tuple(ch[0] for ch in self.model.TYPE_CHOICES)
        if organisation_type not in valid_type_vals:
            raise ValueError(
                "'{}' is not a valid organisation type. Valid values are: {}"
                .format(organisation_type, valid_type_vals)
            )
        return Q(organisation_type__exact=organisation_type)

    def of_type(self, organisation_type):
        return self.filter(self.of_type_q(organisation_type))

    def not_of_type(self, organisation_type):
        return self.exclude(self.of_type_q(organisation_type))

    def for_regions_q(self, *region_vals):
        from .models import Region

        region_ids = set()
        region_codes = set()
        for val in region_vals:
            if isinstance(val, Region):
                region_ids.add(val.id)
            elif isinstance(val, UUID):
                region_ids.add(val)
            elif isinstance(val, str):
                if len(val) <= 20:
                    region_codes.add(val)
                else:
                    region_ids.add(UUID(val, version=4))

        q = Q(region_new_id__in=region_ids)
        if region_codes:
            q |= Q(region_new__code__in=region_codes)
        return q

    def for_regions(self, *region_vals):
        return self.filter(self.for_regions_q(*region_vals))

    def not_for_regions(self, *region_vals):
        return self.exclude(self.for_regions_q(*region_vals))

    @staticmethod
    def choice_label_for_obj(format_string, obj, mark_closed, closed_string):
        label = format_html(
            format_string,
            name=obj.name,
            code=obj.code,
            id=obj.id,
            region=obj.region,
            region_label=obj.get_region_display(),
            type=obj.organisation_type,
            type_label=obj.get_organisation_type_display(),
        )
        if mark_closed and obj.is_closed:
            label += mark_safe(closed_string)
        return label

    def as_choices(
        self, value_field='id', label_format="{name} ({code})",
        group_by_region=False, group_by_type=False, mark_closed=True,
        closed_string=" (Closed)", alternative_optgroup_labels=None,
        ordering=('is_closed', 'name')
    ):
        from .models import Region

        queryset = self.all().annotate_with_is_closed()

        group_by_field_name = None
        if group_by_region:
            group_by_field_name = 'region_new_id'
            if alternative_optgroup_labels:
                try:
                    example_val = alternative_optgroup_labels[0][0] or alternative_optgroup_labels[1][0]
                    if len(example_val) <= 20:
                        group_by_field_name = 'region'
                except KeyError:
                    pass

        if group_by_type:
            group_by_field_name = 'organisation_type'

        if ordering:
            queryset = queryset.order_by(*ordering)

        choices = []
        if group_by_field_name:
            choices = defaultdict(list)
            if alternative_optgroup_labels is None:
                if group_by_field_name == 'region_new_id':
                    optgroup_labels = Region.objects.in_use().as_choices(
                        add_blank_choice=True,
                        blank_choice_label=_('Non-Regional'),
                    )
                else:
                    f = self.model._meta.get_field(group_by_field_name)
                    optgroup_labels = f.choices
            else:
                optgroup_labels = alternative_optgroup_labels

        for obj in queryset:
            choice = (
                getattr(obj, value_field),
                self.choice_label_for_obj(
                    label_format, obj, mark_closed, closed_string
                )
            )
            if group_by_field_name:
                grouping_value = getattr(obj, group_by_field_name)
                choices[grouping_value].append(choice)
            else:
                choices.append(choice)

        if group_by_field_name:
            return [
                (mark_safe(label), choices[val])
                for val, label in optgroup_labels if val in choices
            ]
        return choices

    def as_dict(self, keyed_by='id'):
        return {getattr(obj, keyed_by): obj for obj in self.all()}
