from django.forms import ModelForm
from .models import Event, EventGroup


class EventForm(ModelForm):
    class Meta:
        exclude = ('slug',)
        model = Event

class EventGroupForm(ModelForm):
    class Meta:
        exclude = ('slug',)
        model = EventGroup
