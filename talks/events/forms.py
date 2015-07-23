from django import forms
from django.utils.safestring import mark_safe

from talks.events import typeahead, datasources

from talks.contributors.forms import BootstrappedDateTimeWidget, OxPointField


class BrowseEventsForm(forms.Form):
    start_date = forms.DateTimeField(label="Start Date",
    								 required=False, 
    								 widget=BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'form-control'}))
    to = forms.DateTimeField(label="End Date",
    						 required=False, 
    						 help_text="Choose date range to filter by.",
    						 widget=BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'form-control'}))
    venue = OxPointField(datasources.LOCATION_DATA_SOURCE,
                            	label="Venue",
                            	required=False,
#                            	attrs={'class': 'form-control'},
                            	help_text="Type building name and select from the list.")
    