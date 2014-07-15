from django import forms
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.conf import settings

from talks.api_ox.models import Location, Organisation
from .models import Event, EventGroup, Speaker
from talks.events.models import Topic


class BootstrappedDateTimeWidget(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrappedDateTimeWidget, self).render(name, value, attrs)
        html = """<div class="input-group">
                <span class="input-group-btn">
                    <button class="btn btn-default js-open-calendar" type="button"><span class="glyphicon glyphicon-calendar"></span></button>
                </span>
        """ + html + "</div>"
        return mark_safe(html)


class ModelCommaSeparatedChoiceField(forms.ModelMultipleChoiceField):
    widget = forms.HiddenInput

    def clean(self, value):
        if value:
            value = [item.strip() for item in value.split(",")]
        return super(ModelCommaSeparatedChoiceField, self).clean(value)


class APIOxField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.Model = kwargs.pop('Model', [])
        self.types = kwargs.pop('types', [])
        self.endpoint = kwargs.pop(
            'endpoint', 'http://api.m.ox.ac.uk/places/suggest')
        return super(APIOxField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return super(APIOxField, self).clean(
            self.Model.objects.get_or_create(identifier=value)[0].pk)


class TopicsField(ModelCommaSeparatedChoiceField):
    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.pop('endpoint', settings.TOPICS_URL)
        return super(TopicsField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        if value:
            value = [item.strip() for item in value.split(",")]
        return super(TopicsField, self).clean([Topic.objects.get_or_create(uri=v)[0].pk
                                               for v in value])


class SpeakerTypeaheadInput(forms.TextInput):
    class Media:
        js = ('js/speaker-typeahead.js',)


class TopicTypeaheadInput(forms.TextInput):
    class Media:
        js = ('js/speaker-typeahead.js',)


class EventForm(forms.ModelForm):
    speaker_suggest = forms.CharField(
        label="Speaker",
        help_text="Type speakers name and select from the list.",
        required=False,
        widget=SpeakerTypeaheadInput(attrs={'class': 'js-speakers-typeahead'}),
    )
    speakers = ModelCommaSeparatedChoiceField(
        queryset=Speaker.objects.all(),
        required=False)

    topic_suggest = forms.CharField(
        label="Topic",
        help_text="Type topic name and select from the list",
        required=False,
        widget=TopicTypeaheadInput(attrs={'class': 'js-topics-typeahead'}),
    )
    topics = TopicsField(
        queryset=Topic.objects.all(),
        required=False,
    )

    location_suggest = forms.CharField(
        label="Venue",
        required=False,
        widget=forms.TextInput(attrs={'class': 'js-location-typeahead'}),
    )
    location = APIOxField(
        Model=Location,
        queryset=Location.objects.all(),
        required=False,
        types=['/university/building', '/university/site', '/leisure/museum', '/university/college', '/university/library'],
        widget=forms.HiddenInput(attrs={'class': 'js-location'}),
    )

    department_suggest = forms.CharField(
        label="Department",
        required=False,
        widget=forms.TextInput(attrs={'class': 'js-organisation-typeahead'}),
    )
    department_organiser = APIOxField(
        Model=Organisation,
        queryset=Organisation.objects.all(),
        required=False,
        types=['/university/department', '/university/museum', '/university/college'],
        widget=forms.HiddenInput(attrs={'class': 'js-organisation'}),
    )

    class Media:
        js = ('js/location-typeahead.js',)

    class Meta:
        exclude = ('slug',)
        model = Event
        labels = {
            'description': 'Abstract',
        }
        widgets = {
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
    SELECT_CREATE_CHOICES = ((SELECT, "Add to existing group of talks"),
                             (CREATE, "Create new group of talks"))

    # Does the user want to add this Event to an EventGroup
    enabled = forms.BooleanField(label='Add to a group of talks?',
                                 help_text="e.g. Seminar series, conference",
                                 required=False,
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
        fields = ('event_group_select', 'title', 'group_type', 'description')
        model = EventGroup
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(),
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
        return self.is_enabled()

    def show_create_form(self):
        if self.show_form():
            return any([self.errors.get(field, None) for field in ['title', 'description']])
        return False

    def remove_errors(self):
        """Remove any errors in the form for when it's not enabled"""
        self.errors['title'] = self.error_class()
        self.errors['description'] = self.error_class()

    def clean(self):
        """Used to validate the form over many fields"""
        cleaned_data = super(EventGroupForm, self).clean()
        if self.is_enabled():
            select_create = cleaned_data.get('select_create', None)
            if select_create == self.CREATE:
                return cleaned_data
            elif select_create == self.SELECT:
                self.remove_errors()
                if not cleaned_data.get('event_group_select', None):
                    # Set an error if event group is selected
                    self.add_error('event_group_select', "This field is required.")
                return cleaned_data
        else:
            self.remove_errors()
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
        return self.is_bound and 'enabled' in self.cleaned_data and self.cleaned_data['enabled']


class SpeakerQuickAdd(forms.ModelForm):
    class Meta:
        fields = ('name', 'email_address')
        model = Speaker

    class Media:
        js = ('js/speaker-quick-add.js',)
