from django import forms
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.forms.widgets import Select, RadioSelect
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from talks.events import models, typeahead, datasources
from talks.events.models import EventGroup, AUDIENCE_CHOICES, AUDIENCE_PUBLIC, AUDIENCE_OXFORD, AUDIENCE_OTHER
from talks.users.authentication import GROUP_EDIT_EVENTS
from talks.core.utils import clean_xml

class OxPointField(forms.CharField):
    def __init__(self, source, *args, **kwargs):
        self.widget = typeahead.Typeahead(source)
        return super(OxPointField, self).__init__(*args, **kwargs)


class TopicsField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True

class XMLFriendlyTextField(forms.CharField):
    def clean(self, data):
        super(XMLFriendlyTextField, self).clean(data)
        return clean_xml(data)
        

class BootstrappedDateTimeWidget(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrappedDateTimeWidget, self).render(name, value, attrs)
        html = """<div class='input-group date js-datetimepicker' id='""" + name + """'>
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
        """ + html + "</div>"

        return mark_safe(html)


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super(EventForm, self).__init__(*args, **kwargs)
        # Customise the group selector so that:
        #  - It's only possible to pick talks which the user has edit permissions for
        #  - It's not possible to unassign or reassign the group
        if not self.instance.group or self.instance.group.user_can_edit(self.user):
            #user may change the group. Populate the list with only the available choices
            if self.user and self.user.is_superuser:
                self.fields['group'].queryset = models.EventGroup.objects.all().order_by('title')
            else:
                query = Q(editor_set__in=[self.user])
                if self.instance.group:
                    query = query | Q(slug=self.instance.group.slug)
                self.fields['group'].queryset = models.EventGroup.objects.filter(query).distinct().order_by('title')
        else:
            #user should be able to see the field but not be able to edit it
            self.fields['group'].widget.attrs['readonly'] = True

        # Amend help text if no groups to choose from
        if (not self.fields['group'].queryset) or self.fields['group'].queryset.count <= 0:
            self.fields['group'].empty_label = "-- There are no series which you can add this talk to --"

        # set preliminary values for audience_choices and audience_other
        if self.instance.audience == AUDIENCE_PUBLIC:
            self.fields['audience_choices'].initial = 'public'

        elif self.instance.audience == AUDIENCE_OXFORD:
            self.fields['audience_choices'].initial = 'oxonly'

        else:
            self.fields['audience_choices'].initial = 'other'
            self.fields['audience_other'].initial = self.instance.audience



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
                            help_text="Type building name and select from the list.",
                            required=False)

    department_organiser = OxPointField(datasources.DEPARTMENT_DATA_SOURCE,
                                        required=False,
                                        help_text="Type department name and select from the list",
                                        label="Organising department")

    group = forms.ModelChoiceField(
        EventGroup.objects.none(),
        empty_label="-- select a series --",
        widget=Select(attrs={'class': 'form-control'}),
        required=False,
        label="Series",
        help_text="Select from series which you have permission to edit"
    )

    editor_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(Q(is_superuser=True) | Q(groups__name=GROUP_EDIT_EVENTS)).distinct(),
        label="Other Editors",
        help_text="Share editing with another Talks Editor by typing in their email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.USERS_DATA_SOURCE),
    )

    audience = forms.CharField(
        required=False
    )


    audience_choices = forms.ChoiceField(
        label="Who can attend",
        required=False,
        choices=AUDIENCE_CHOICES,
        widget=RadioSelect()
    )

    title = XMLFriendlyTextField(
        max_length=250,
        required=False,
    )

    location_details = XMLFriendlyTextField(
        required=False,
        label='Venue details',
        help_text='e.g.: room number or accessibility information'
    )

    description = XMLFriendlyTextField(
        label="Abstract",
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
    )

    special_message = XMLFriendlyTextField(
        required=False,
        label="Special message",
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Use this for important notices - e.g.: cancellation or a last minute change of venue"
    )

    audience_other = XMLFriendlyTextField(
        label="",
        required=False,
        help_text="If other, please specify"
    )

    cost = XMLFriendlyTextField(
        required=False,
    )

    class Meta:
        exclude = ('slug', 'embargo')
        model = models.Event
        widgets = {
            'start': BootstrappedDateTimeWidget(attrs={'readonly': True}),
            'end': BootstrappedDateTimeWidget(attrs={'readonly': True}),
            'booking_type': forms.RadioSelect,
            'audience': forms.RadioSelect,
            'status': forms.RadioSelect,
        }
        help_texts = {
            'organiser_email': 'Email address for more details',
            'booking_url': 'Provide a website address for booking e.g. "http://www.ox.ac.uk"',
            'booking_email': 'Alternatively, provide an email address for booking',
        }

    def save(self):
        event = super(EventForm, self).save(commit=False)
        # saved with commit=False because of the ManyToMany relations
        # in the model

        # explicitly set audience to the value from cleaned data otherwise it doesn't get set
        event.audience = self.cleaned_data['audience']
        event.save()

        # clear the list of editors and repopulate with the contents of the form
        event.editor_set.clear()
        for user in self.cleaned_data['editor_set']:
            event.editor_set.add(user)

        #reorder the speakers to be in the order they arrived in the post data (after that point the ordering is lost)
        speakers_posted = self.request.POST.copy().pop('event-speakers', [])
        speakers_current = getattr(event, 'speakers')
        speakers_cleaned = self.cleaned_data['speakers']

        #determine if the list of speakers has changed
        should_replace_speakers = False
        if speakers_current.count() != len(speakers_posted):
            #definitely different if lists are different lengths
            should_replace_speakers = True
        else:
            #compare item-by-item to see if lists contain the same elements
            for idx, speaker in enumerate(speakers_current):
                if int(speakers_posted[idx]) != speaker.id:
                    # order is not the same
                    should_replace_speakers = True
                    break

        if should_replace_speakers:
            #remove all speakers
            for person in speakers_current:
                rel = models.PersonEvent.objects.get(person=person, event=event, role=models.ROLES_SPEAKER)
                rel.delete()
            #add new speakers in the order they were in the posted data
            for speaker_id in speakers_posted:
                person = models.Person.objects.get(id=speaker_id)
                models.PersonEvent.objects.create(person=person, event=event, role=models.ROLES_SPEAKER)

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
            raise forms.ValidationError("Either provide the Title or mark it as TBA")

        if self.instance.group and not self.instance.group.user_can_edit(self.user):
            if not self.cleaned_data['group'] is self.instance.group.id:
                #don't allow this user to clear the group
                raise forms.ValidationError("You do not have permission to move this talk from its current series")

        # fill in the 'audience' field used by the model, based on the form values filled in
        if 'audience_choices' in self.cleaned_data and self.cleaned_data['audience_choices'] == 'other':
            if not self.cleaned_data['audience_other'] or self.cleaned_data['audience_other'] == '':
                raise forms.ValidationError("You must specify who can attend")
            else:
                print "setting to value of audience_other field"
                self.cleaned_data['audience'] = self.cleaned_data['audience_other']
        else:
            if 'audience_choices' in self.cleaned_data and not self.cleaned_data['audience_choices'] == '':
                self.cleaned_data['audience'] = self.cleaned_data['audience_choices']

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

    organisers = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        label="Organisers",
        help_text="Type a name and select from the list",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.PERSONS_DATA_SOURCE),
    )

    editor_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(Q(is_superuser=True) | Q(groups__name=GROUP_EDIT_EVENTS)).distinct(),
        label="Other Editors",
        help_text="Share editing with another Talks Editor by typing in their email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.USERS_DATA_SOURCE),
    )

    title = XMLFriendlyTextField(
        max_length=250,
        required=True
    )

    description = XMLFriendlyTextField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
    )

    occurence = XMLFriendlyTextField(
        required=False,
        label='Timing',
        help_text='e.g.: Mondays at 10 or September 19th to 20th.'
    )

    def save(self):
        group = super(EventGroupForm, self).save(commit=False)
        group.save()

        # clear the list of editors and repopulate with the contents of the form
        group.editor_set.clear()
        for user in self.cleaned_data['editor_set']:
            group.editor_set.add(user)

        group.organisers.clear()
        for person in self.cleaned_data['organisers']:
            group.organisers.add(person)

        group.save()
        return group

    class Meta:
        exclude = ('slug',)
        model = models.EventGroup
        labels = {
            'group_type': 'Series type'
        }


class PersonForm(forms.ModelForm):

    class Meta:
        fields = ('name', 'bio', 'web_address')
        model = models.Person
        widgets = {
            'bio': forms.TextInput(),
        }


class PersonQuickAdd(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonQuickAdd, self).__init__(*args, **kwargs)

        self.fields['name'].required = False

    class Meta:
        fields = ('name', 'bio', 'web_address')
        model = models.Person
        widgets = {
            # For an inline form, a placeholder works better than a label
            'name': forms.TextInput(attrs={'placeholder':'Enter Name'}),
            'bio': forms.TextInput(attrs={'placeholder':'Enter Affiliation'}),
            'web_address': forms.TextInput(attrs={'placeholder': 'Enter relevant web address'}),
        }
        labels = {
            'name': "",
            'bio': "",
            'web_address': "",
        }
        help_texts = {
            'name': "e.g. Dr Joseph Bloggs",
            'bio': "e.g. University of Oxford",
            'web_address': "http://en.wikipedia.org/wiki/Example"
        }
