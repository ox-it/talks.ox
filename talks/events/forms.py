from django import forms
from django.utils.safestring import mark_safe

from talks.events import typeahead, datasources

from talks.contributors.forms import BootstrappedDateTimeWidget


class BrowseEventsForm(forms.Form):
    #start_date = forms.CharField(label='Start Date', max_length=100)
    start_date = forms.DateTimeField(required=False, 
    								 widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    end_date = forms.DateTimeField(required=False, 
    							   widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
 