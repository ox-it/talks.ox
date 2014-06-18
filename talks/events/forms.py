from django import forms
from django.utils.safestring import mark_safe

from .models import Event, EventGroup


class BootstrappedDateTimeWidget(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrappedDateTimeWidget, self).render(name, value, attrs)
        html = """<div class="input-group">
                <span class="input-group-btn">
                    <button class="btn btn-default js-open-calendar" type="button"><span class="glyphicon glyphicon-calendar"></span></button>
                </span>
        """ + html + "</div>"
        return mark_safe(html)


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
            'start': BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'js-datetimepicker event-start'}),
            'end': BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'js-datetimepicker event-end'}),
        }

class EventGroupForm(forms.ModelForm):
    """We extend this ModelForm to add the following features:

      - enabled: a special boolean, if not set then the form is always valid
                 and has no effect.
      - event_group_select: rather than creating a new EventGroup the user can
                            select an existing group.
    """
    SELECT = 'SEL'
    CREATE = 'CRE'
    SELECT_CREATE_CHOICES = ((SELECT, "Add to existing event group"),
                             (CREATE, "Create new event group"))

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

    def is_valid(self):
        """Override the ModelForm is_valid so we can handle our special
        behaviour. Our form is only valid if it is enabled. Even then it
        depends if the user is selecting an EventGroup or creating one from
        scratch.
        """
        valid = super(EventGroupForm, self).is_valid()
        if self.is_enabled():
            select_create = self.cleaned_data.get('select_create', None)
            if select_create == self.CREATE:
                return valid
            elif select_create == self.SELECT and self.cleaned_data.get('event_group_select', None):
                # So long as a event_group_select has been input
                return True
        else:
            # Always valid if we are not enabled
            return True
        return False

    def show_form(self):
        return bool(self.errors or self.initial)

    def show_create_form(self):
        if self.show_form():
            return any([self.errors.get(field, None) for field in ['title', 'description']])
        return False

    def clean(self):
        """Used to validate the form over many fields"""
        cleaned_data = super(EventGroupForm, self).clean()
        if self.is_enabled():
            select_create = cleaned_data.get('select_create', None)
            if select_create == self.CREATE:
                return cleaned_data
            elif select_create == self.SELECT:
                # Remove any errors in the form
                self.errors['title'] = self.error_class()
                self.errors['description'] = self.error_class()
                if not cleaned_data.get('event_group_select', None):
                    # Set an error if event group is selected
                    self.add_error('event_group_select', "This field is required.")
                return cleaned_data
        else:
            return {}


    def get_event_group(self):
        """Get the selected event group or create a new one

        NOTE: if an EventGroup is created we don't commit it to the database
              here, that is the responsibility of the view.
        """
        valid = self.is_valid()
        if self.is_enabled():
            select_create = self.cleaned_data.get('select_create', None)
            if select_create == self.SELECT:
                if 'event_group_select' in self.cleaned_data and self.cleaned_data['event_group_select']:
                    return self.cleaned_data['event_group_select']
                else:
                    return None
            elif valid and select_create == self.CREATE:
                return self.save(commit=False)
        return None

    def is_enabled(self):
        return 'enabled' in self.cleaned_data
