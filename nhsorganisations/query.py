from collections import defaultdict

from django.db.models import Case, IntegerField, Q, QuerySet, When
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class OrganisationQuerySet(QuerySet):

    def open_q(self, until_datetime):
        return Q(closure_date__isnull=True) | Q(closure_date__gt=until_datetime)

    def open(self):
        return self.filter(self.open_q(until_datetime=timezone.now()))

    def closed(self):
        return self.exclude(self.open_q(until_datetime=timezone.now()))

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

    def for_regions(self, *regions):
        if len(regions) == 1:
            return self.filter(region__exact=regions[0])
        return self.filter(region__in=regions)

    def not_for_regions(self, *regions):
        if len(regions) == 1:
            return self.exclude(region__exact=regions[0])
        return self.exclude(region__in=regions)

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
        group_by_field_name = None
        if group_by_region:
            group_by_field_name = 'region'
        if group_by_type:
            group_by_field_name = 'organisation_type'

        queryset = self.all().annotate(is_closed=Case(
            When(closure_date__isnull=True, then=0),
            default=1,
            output_field=IntegerField()
        ))
        if ordering:
            queryset = queryset.order_by(*ordering)

        choices = []
        if group_by_field_name:
            choices = defaultdict(list)
            if alternative_optgroup_labels is None:
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
