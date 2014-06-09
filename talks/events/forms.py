from django import forms

from .models import Event, EventGroup


class EventForm(forms.ModelForm):

    class Meta:
        fields = ('title', 'description', 'speakers', 'location', 'start', 'end')
        model = Event
        labels = {
            'description': 'Abstract',
            'speakers': 'Speaker',
            'location': 'Venue',
        }
        widgets = {
            'speakers': forms.TextInput,
            'location': forms.TextInput,
        }

class EventGroupForm(forms.ModelForm):
    enabled = forms.BooleanField(label='Add to a group?')
    form_enabled = forms.CharField(widget=forms.HiddenInput)
    select_enabled = forms.CharField(widget=forms.HiddenInput)
    event_group_select = forms.ModelChoiceField(
            queryset=EventGroup.objects.all(),
            required=False,
            label="Existing group")

    class Meta:
        fields = ('form_enabled', 'select_enabled', 'event_group_select', 'title', 'description')
        model = EventGroup
