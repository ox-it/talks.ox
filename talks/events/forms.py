from urllib import urlencode

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from talks.api import serializers

from . import models, typeahead
from talks.users.authentication import GROUP_EDIT_EVENTS


class OxPointDataSource(typeahead.DataSource):
    def __init__(self, **kwargs):
        _types = kwargs.pop('types', [])
        url = settings.API_OX_PLACES_URL + "suggest?" + urlencode({'type_exact': _types}, doseq=True) + '&q=%QUERY'
        super(OxPointDataSource, self).__init__(
            'oxpoints',
            url=url,
            response_expression='response._embedded.pois',
            # XXX: forcing api to return list if requesting single object
            get_prefetch_url=lambda values: settings.API_OX_PLACES_URL + ",".join(values) + ","
        )

LOCATION_DATA_SOURCE = OxPointDataSource(
    types=['/university/building', '/university/site', '/leisure/museum', '/university/college', '/university/library']
)
DEPARTMENT_DATA_SOURCE = OxPointDataSource(
    types=['/university/department', '/university/museum', '/university/college', '/university/hall',
           '/university/division']
)
TOPICS_DATA_SOURCE = typeahead.DataSource(
    'topics',
    url=settings.TOPICS_URL + "suggest?count=10&q=%QUERY",
    get_prefetch_url=lambda values: ("%sget?%s" % (settings.TOPICS_URL, urlencode({'uri': values}, doseq=True))),
    display_key='prefLabel',
    id_key='uri',
    response_expression='response._embedded.concepts',
)
SPEAKERS_DATA_SOURCE = typeahead.DjangoModelDataSource(
    'speakers',
    url='/events/persons/suggest?q=%QUERY',
    display_key='title',
    serializer=serializers.PersonSerializer,
)
USERS_DATA_SOURCE = typeahead.DjangoModelDataSource(
    'users',
    url='/api/user/suggest?q=%QUERY',
    display_key='email',
    serializer=serializers.UserSerializer
)


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
        widget=typeahead.MultipleTypeahead(SPEAKERS_DATA_SOURCE),
    )

    topics = TopicsField(
        label="Topics",
        help_text="Type topic name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(TOPICS_DATA_SOURCE),
    )

    location = OxPointField(LOCATION_DATA_SOURCE,
                            label="Venue",
                            help_text="Type location name and select from the list",
                            required=False)

    department_organiser = OxPointField(DEPARTMENT_DATA_SOURCE,
                                        required=False,
                                        help_text="Type department name and select from the list",
                                        label="Organising department")

    group = forms.ModelChoiceField(
        models.EventGroup.objects.all(),
        empty_label="-- select a group --",
        widget=Select(attrs={'class': 'form-control'}),
        required=False,
    )

    editor_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(Q(is_superuser=True) | Q(groups__name=GROUP_EDIT_EVENTS)).distinct(),
        label="Other event organisers who can edit this event",
        help_text="Type an event organiser's email address",
        required=False,
        widget=typeahead.MultipleTypeahead(USERS_DATA_SOURCE),
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

    def save(self):
        event = super(EventForm, self).save(commit=False)
        # saved with commit=False because of the ManyToMany relations
        # in the model
        event.save()

        # clear the list of editors and repopulate with the contents of the form
        event.editor_set.clear()
        for user in self.cleaned_data['editor_set']:
            event.editor_set.add(user)

        current_speakers = event.speakers
        form_speakers = self.cleaned_data['speakers']
        for person in form_speakers:
            models.PersonEvent.objects.get_or_create(person=person, event=event, role=models.ROLES_SPEAKER)
        for person in current_speakers:
            if person not in form_speakers:
                rel = models.PersonEvent.objects.get(person=person, event=event, role=models.ROLES_SPEAKER)
                rel.delete()

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


class EventGroupForm(forms.ModelForm):

    department_organiser = OxPointField(DEPARTMENT_DATA_SOURCE, required=False, label="Organising department")

    organiser = forms.ModelChoiceField(
        queryset=models.Person.objects.all(),
        label="Organiser",
        help_text="Type a name and select from the list",
        required=False,
        widget=typeahead.Typeahead(SPEAKERS_DATA_SOURCE),
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
        fields = ('name', 'bio', 'email_address')
        model = models.Person
        widgets = {
            'bio': forms.TextInput(),
        }
