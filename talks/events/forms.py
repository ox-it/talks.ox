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

class EnableEventGroupForm(forms.Form):
    enabled = forms.BooleanField(label='Add to a group?')

class EventGroupForm(forms.ModelForm):
    enabled = forms.BooleanField(required=False)

    class Meta:
        fields = ('enabled', 'title', 'description')
        model = EventGroup

class EventGroupSelectForm(forms.Form):
    enabled = forms.BooleanField(required=False)
    event_group = forms.ModelChoiceField(queryset=EventGroup.objects.all(),
                                         required=False,
                                         label="Existing group")
    class Meta:
        fields = ('enabled', 'event_group')
