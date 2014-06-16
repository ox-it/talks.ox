from django import forms

from .models import Event, EventGroup


class EventForm(forms.ModelForm):

    class Meta:
        fields = ('title', 'start', 'end', 'description', 'speakers', 'location')
        model = Event
        labels = {
            'description': 'Abstract',
            'speakers': 'Speaker',
            'location': 'Venue',
        }
        widgets = {
            'speakers': forms.TextInput,
            'location': forms.TextInput,
            'start': forms.DateTimeInput(attrs={'readonly': True, 'class': 'js-datetimepicker event-start'}),
            'end': forms.DateTimeInput(attrs={'readonly': True, 'class': 'js-datetimepicker event-end'}),
        }

class EventGroupForm(forms.ModelForm):
    SELECT_CREATE_CHOICES = (('SEL', "Add to existing event group"),
                             ('CRE', "Create new event group"))

    # Does the user want to add this Event to an EventGroup
    enabled = forms.BooleanField(label='Add to a group?',
                                 widget=forms.CheckboxInput(attrs={'autocomplete': 'off'}))


    # Is the user filling in the ModelForm to create a new EventGroup
    # Is the user selecting an existing EventGroup to add the Event to
    select_create = forms.ChoiceField(choices=SELECT_CREATE_CHOICES,
                                      initial='SEL',
                                      widget=forms.RadioSelect(attrs={'autocomplete': 'off'}))

    event_group_select = forms.ModelChoiceField(
            queryset=EventGroup.objects.all(),
            required=False,
            label="Existing group")

    class Meta:
        fields = ('event_group_select', 'title', 'description')
        model = EventGroup
        widgets = {
            'title': forms.TextInput(attrs={'disabled': True}),
            'description': forms.Textarea(attrs={'disabled': True}),
        }

    def clean(self):
        cleaned_data = super(EventGroupForm, self).clean()
        if 'enabled' in cleaned_data:
            if 'form_enabled' in cleaned_data:
                return cleaned_data
            elif 'select_enabled' in cleaned_data:
                self.errors['title'] = None
                self.errors['description'] = None
                if not cleaned_data.get('event_group_select', None):
                    self.add_error('event_group_select', "Select an Event Group")
                return cleaned_data
        else:
            return {}


    def get_event_group(self):
        # Form has been completed and user has selected an event group
        valid = self.is_valid()
        if 'enabled' in self.cleaned_data:
            # Creating a new EventGroup
            if valid and 'form_enabled' in self.cleaned_data:
                return self.save(commit=False)
            elif 'select_enabled' in self.cleaned_data and 'event_group_select' in self.cleaned_data:
                return self.cleaned_data['event_group_select']
        return None

    def is_enabled(self):
        self.is_valid()
        return 'enabled' in self.cleaned_data
