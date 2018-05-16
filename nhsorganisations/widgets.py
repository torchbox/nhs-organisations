from django import forms
from django.utils.functional import cached_property
from .models import Organisation

MEDIA_BASE_DIR = 'nhsorganisations/widgets/'


class GroupedOrganisationSelectMixin:

    default_label_format = "{name} ({code})"

    def __init__(self, *args, **kwargs):
        self.value_field = kwargs.pop('value_field', 'id')
        self.label_format = kwargs.pop('label_format', self.default_label_format)
        self.group_by_region = kwargs.pop('group_by_region', False)
        self.group_by_type = kwargs.pop('group_by_type', False)
        self.alternative_optgroup_labels = kwargs.pop('alternative_optgroup_labels', None)
        self.mark_closed = kwargs.pop('mark_closed', True)
        self.closed_string = kwargs.pop('closed_string', None)
        if self.group_by_type:
            self.group_by_region = False
        if self.alternative_optgroup_labels is None:
            if self.group_by_region:
                self.alternative_optgroup_labels = Organisation.REGION_CHOICES_OPTGROUPS
            elif self.group_by_type:
                self.alternative_optgroup_labels = Organisation.TYPE_CHOICES_PLURALISED

        if 'ordering' in kwargs:
            self.ordering = kwargs['ordering']
        else:
            self.ordering = ('is_closed', 'name')
        super().__init__(*args, **kwargs)

    @cached_property
    def grouped_organisation_choices(self):
        return Organisation.objects.as_choices(
            value_field=self.value_field,
            label_format=self.label_format,
            group_by_region=self.group_by_region,
            group_by_type=self.group_by_type,
            alternative_optgroup_labels=self.alternative_optgroup_labels,
            mark_closed=self.mark_closed,
            closed_string=self.closed_string,
            ordering=self.ordering,
        )

    def render(self, *args, **kwargs):
        self.choices = self.grouped_organisation_choices
        return super().render(*args, **kwargs)


class OrganisationCheckboxSelectMultiple(
    GroupedOrganisationSelectMixin, forms.CheckboxSelectMultiple
):
    default_label_format = "{name} <code>{code}</code>"

    class Media:
        css = {
            'all': (
                '{}organisationcheckboxselectmultiple/widget.css'.format(MEDIA_BASE_DIR),
            )
        }
        js = (
            '{}organisationcheckboxselectmultiple/widget.js'.format(MEDIA_BASE_DIR),
        )
