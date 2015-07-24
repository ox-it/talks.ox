from django import forms
from django.utils.safestring import mark_safe

from talks.events import typeahead, datasources

from talks.contributors.forms import BootstrappedDateTimeWidget, OxPointField


class BrowseEventsForm(forms.Form):
    start_date = forms.DateTimeField(label="Start Date",
                                     required=True,
                                     widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    to = forms.DateTimeField(label="End Date",
                             required=False,
                             help_text="Choose date range to filter by.",
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
