from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from talks.events import typeahead, datasources

from talks.contributors.forms import BootstrappedDateTimeWidget, OxPointField

class BrowseSeriesForm(forms.Form):
    seriesslug = OxPointField(datasources.SERIES_DATA_SOURCE_BY_SLUG,
                                         label="Find a Series",
                                         required=False,
                                         help_text='Type series name and select from the list.')  


class BrowseEventsForm(forms.Form):
    start_date = forms.DateTimeField(label="Start Date",
                                     required=True,
                                     widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    to = forms.DateTimeField(label="End date",
                             required=False,
                             widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    venue = OxPointField(datasources.LOCATION_DATA_SOURCE,
                         label="Venue",
                         required=False,
                         help_text="Type building name and select from the list.")
    organising_department = OxPointField(datasources.DEPARTMENT_DATA_SOURCE,
                                         label="Department",
                                         required=False,
                                         help_text="Type department name and select from the list.")
    include_subdepartments = forms.BooleanField(label="Include sub-departments?",
                                        initial=True,
                                        required=False)
    seriesid = OxPointField(datasources.SERIES_DATA_SOURCE,
                                         label="Series",
                                         required=False,
                                         help_text="Type series name and select from the list.")

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('to')

        if not start_date:
            raise ValidationError({'start_date': 'Start date is required'})

        # Ensure end date is after start date
        if end_date and (end_date < start_date):
            raise ValidationError({'to': 'End date must be after start date'})
