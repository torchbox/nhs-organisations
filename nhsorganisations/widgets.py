from django import forms
from django.utils.functional import cached_property
from .models import Organisation

MEDIA_BASE_DIR = 'nhsorganisations/widgets/'


class GroupedOrganisationSelectMixin:

    allow_html_in_labels = False

    def __init__(self, *args, **kwargs):
        self.optgroup_choices = kwargs.pop('optgroup_choices', None)
        self.group_by_region = kwargs.pop('grouped_by_region', False)
        self.group_by_type = kwargs.pop('group_by_type', False)
        if self.group_by_type:
            self.group_by_region = False
        if self.optgroup_choices is None:
            if self.group_by_region:
                self.optgroup_choices = Organisation.REGION_CHOICES_OPTGROUPS
            elif self.group_by_type:
                self.optgroup_choices = Organisation.TYPE_CHOICES_PLURALISED
        self.add_org_code_to_labels = kwargs.pop('add_org_code_to_labels', True)
        self.limit_to = kwargs.pop('limit_to', None)
        super().__init__(*args, **kwargs)

    @cached_property
    def grouped_organisation_choices(self):
        return Organisation.objects.as_choices(
            group_by_region=self.group_by_region,
            group_by_type=self.group_by_type,
            limit_to=self.limit_to,
            add_org_code_to_labels=self.add_org_code_to_labels,
            use_code_tags=self.allow_html_in_labels,
            optgroup_label_choices=self.optgroup_choices,
        )

    def render(self, *args, **kwargs):
        self.choices = self.grouped_organisation_choices
        return super().render(*args, **kwargs)


class OrganisationCheckboxSelectMultiple(
    GroupedOrganisationSelectMixin, forms.CheckboxSelectMultiple
):
    allow_html_in_labels = True

    class Media:
        css = {
            'all': (
                '{}organisationcheckboxselectmultiple/widget.css'.format(MEDIA_BASE_DIR),
            )
        }
        js = (
            '{}organisationcheckboxselectmultiple/widget.js'.format(MEDIA_BASE_DIR),
        )
