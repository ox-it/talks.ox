from django import forms
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from talks.events import models, typeahead, datasources
from talks.users.authentication import GROUP_EDIT_EVENTS


class OxPointField(forms.CharField):
    def __init__(self, source, *args, **kwargs):
        self.widget = typeahead.Typeahead(source)
        return super(OxPointField, self).__init__(*args, **kwargs)


class TopicsField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True


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
    speakers = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        label="Speakers",
        help_text="Type speaker name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.PERSONS_DATA_SOURCE),
    )

    organisers = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        label="Organisers",
        help_text="Type organiser name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.PERSONS_DATA_SOURCE),
    )

    hosts = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        label="Hosts",
        help_text="Type host name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.PERSONS_DATA_SOURCE),
    )

    topics = TopicsField(
        label="Topics",
        help_text="Type topic name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.TOPICS_DATA_SOURCE),
    )

    location = OxPointField(datasources.LOCATION_DATA_SOURCE,
                            label="Venue",
                            help_text="Type location name and select from the list",
                            required=False)

    department_organiser = OxPointField(datasources.DEPARTMENT_DATA_SOURCE,
                                        required=False,
                                        help_text="Type department name and select from the list",
                                        label="Organising department")

    group = forms.ModelChoiceField(
        models.EventGroup.objects.all(),
        empty_label="-- select a series --",
        widget=Select(attrs={'class': 'form-control'}),
        required=False,
        label="Series",
        to_field_name="slug"
    )

    editor_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(Q(is_superuser=True) | Q(groups__name=GROUP_EDIT_EVENTS)).distinct(),
        label="Other event organisers who can edit this event",
        help_text="Type an event organiser's email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.USERS_DATA_SOURCE),
    )

    class Meta:
        exclude = ('slug', 'embargo')
        model = models.Event
        labels = {
            'description': 'Abstract',
        }
        widgets = {
            'start': BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'js-datetimepicker event-start'}),
            'end': BootstrappedDateTimeWidget(attrs={'readonly': True, 'class': 'js-datetimepicker event-end'}),
            'booking_type': forms.RadioSelect,
            'cost': forms.TextInput,
            'audience': forms.RadioSelect,
            'location_details': forms.TextInput,
            'status': forms.RadioSelect
        }
        help_texts = {
            'organiser_email': 'Option email address via which the organiser can be contacted',
            'booking_url': 'Provide a url for a website where users can book a place',
            'booking_email': 'Alternatively, provide an Email address users should contact to book a place',
        }

    def save(self):
        event = super(EventForm, self).save(commit=False)
        # saved with commit=False because of the ManyToMany relations
        # in the model
        event.save()

        # clear the list of editors and repopulate with the contents of the form
        event.editor_set.clear()
        for user in self.cleaned_data['editor_set']:
            event.editor_set.add(user)

        self._update_people('speakers', event, models.ROLES_SPEAKER)
        self._update_people('organisers', event, models.ROLES_ORGANISER)
        self._update_people('hosts', event, models.ROLES_HOST)

        current_topics_uris = [t.uri for t in event.topics.all()]
        form_topics = self.cleaned_data['topics']
        event_ct = ContentType.objects.get_for_model(models.Event)
        for topic in form_topics:
            models.TopicItem.objects.get_or_create(uri=topic,
                                                   content_type=event_ct,
                                                   object_id=event.id)
        for topic_uri in current_topics_uris:
            if topic_uri not in form_topics:
                ti = models.TopicItem.objects.get(uri=topic_uri,
                                                  content_type=event_ct,
                                                  object_id=event.id)
                ti.delete()

        event.save()
        return event

    def clean(self):
        if not self.cleaned_data['title'] and not self.cleaned_data['title_not_announced']:
            raise forms.ValidationError("Either provide title or mark it as not announced")
        return self.cleaned_data

    def _update_people(self, field, event, role):
        """
        Update the Persons for the given event model based on this form, creating/deleting PersonEvents as required
        :param field: the name of the form field and model field, e.g. 'speakers'
        :param event: the event being updated
        :param role: the relevant role for the given field
        :return:
        """
        form_people = self.cleaned_data[field]
        current_people = getattr(event, field)
        for person in form_people:
            models.PersonEvent.objects.get_or_create(person=person, event=event, role=role)
        for person in current_people:
            if person not in form_people:
                rel = models.PersonEvent.objects.get(person=person, event=event, role=role)
                rel.delete()


class EventGroupForm(forms.ModelForm):

    department_organiser = OxPointField(datasources.DEPARTMENT_DATA_SOURCE, required=False, label="Organising department")

    organiser = forms.ModelChoiceField(
        queryset=models.Person.objects.all(),
        label="Organiser",
        help_text="Type a name and select from the list",
        required=False,
        widget=typeahead.Typeahead(datasources.PERSONS_DATA_SOURCE),
    )

    class Meta:
        # fields = ('title', 'group_type', 'description', 'organiser', 'occurence', 'web_address')
        exclude = ('slug',)
        model = models.EventGroup
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(),
            'occurence': forms.TextInput(),
        }


class PersonForm(forms.ModelForm):

    class Meta:
        fields = ('name', 'bio',)
        model = models.Person
        widgets = {
            'bio': forms.TextInput(),
        }


class PersonQuickAdd(forms.ModelForm):
    class Meta:
        fields = ('name', 'bio')
        model = models.Person
        widgets = {
            # For an inline form, a placeholder works better than a label
            'name': forms.TextInput(attrs={'placeholder':'Enter Name'}),
            'bio': forms.TextInput(attrs={'placeholder':'Enter Affiliation'}),
        }
        labels = {
            'name': "",
            'bio': "",
        }
        help_texts = {
            'name': "e.g. Dr Joseph Bloggs",
            'bio': "e.g. University of Oxford"
        }
