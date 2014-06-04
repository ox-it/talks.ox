from django import forms

from .models import Event, EventGroup


class EventGroupSelectForm(forms.Form):
    event_group = forms.ModelChoiceField(queryset=EventGroup.objects.all(),
                                         required=False,
                                         label="Existing group")

class EventForm(forms.ModelForm):
    class Meta:
        fields = ['title', 'description', 'speakers', 'location', 'start', 'end']
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
    class Meta:
        exclude = ('slug',)
        model = EventGroup
