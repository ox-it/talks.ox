from django import forms
from django.conf import settings
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from . import models


class Typeahead(forms.HiddenInput):
    class Media:
        js = ('js/element-typeahead.js',)

    def __init__(self, source, attrs=None):
        self.source = source
        if attrs is None:
            attrs = {}
        class_names = attrs.pop('class', '').split()
        class_names.append("ftypeahead")
        attrs['class'] = " ".join(class_names)
        super(Typeahead, self).__init__(attrs)


class MultipleTypeahead(Typeahead):
    def value_from_datadict(self, data, files, name):
        if hasattr(data, 'getlist'):
            return data.getlist(name)
        return data.get(name, None)

class BootstrappedDateTimeWidget(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrappedDateTimeWidget, self).render(name, value, attrs)
        html = """<div class="input-group">
                <span class="input-group-btn">
                    <button class="btn btn-default js-open-calendar" type="button"><span class="glyphicon glyphicon-calendar"></span></button>
                </span>
        """ + html + "</div>"
        return mark_safe(html)


class DataSource(object):

    def __init__(self, query_url):
        self.query_url = query_url


from urllib import urlencode


class DjangoInternalDataSource(object):
    def __init__(self, view):
        self._view = view

    @property
    def query_url(self):
        from django.core.urlresolvers import reverse
        return reverse(self.view)


class OxPointDataSource(DataSource):
    def __init__(self, **kwargs):
        self._types = kwargs.pop('types', [])
        self._endpoint = kwargs.pop('endpoint', '//api.m.ox.ac.uk/places/suggest')

    @property
    def query_url(self):
        return self._endpoint + "?" + urlencode({'type_exact': self._types}, doseq=True)


LOCATION_DATA_SOURCE = OxPointDataSource(types=['/university/building', '/university/site', '/leisure/museum', '/university/college', '/university/library'])
DEPARTMENT_DATA_SOURCE = OxPointDataSource(types=['/university/department', '/university/museum', '/university/college'])
TOPICS_DATA_SOURCE = DataSource(settings.TOPICS_URL)
SPEAKERS_DATA_SOURCE = DjangoInternalDataSource('suggest-speaker')


class OxPointField(forms.CharField):
    def __init__(self, source, *args, **kwargs):
        self.widget = Typeahead(source)
        return super(OxPointField, self).__init__(*args, **kwargs)


class TopicsField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True


class EventForm(forms.ModelForm):
    speakers = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        label="Speaker",
        help_text="Type speakers name and select from the list.",
        required=False,
        widget=MultipleTypeahead(None),
    )

    topics = TopicsField(
        label="Topic",
        help_text="Type topic name and select from the list",
        required=False,
        widget=MultipleTypeahead(TOPICS_DATA_SOURCE),
    )

    location = OxPointField(LOCATION_DATA_SOURCE, label="Venue", required=False)
    department_organiser = OxPointField(LOCATION_DATA_SOURCE, required=False, label="Department")

    group = forms.ModelChoiceField(
        models.EventGroup.objects.all(),
        empty_label="-- select a group --",
        widget=Select(attrs={'class': 'form-control'}),
        required=False,
    )

    class Media:
        js = ('js/location-typeahead.js',)

    class Meta:
        exclude = ('slug',)
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
        }

    def save(self):
        event = super(EventForm, self).save(commit=False)
        event.save()
        for person in self.cleaned_data['speakers']:
            models.PersonEvent.objects.create(person=person, event=event, role=models.ROLES_SPEAKER)
        event_topics = self.cleaned_data['topics']
        event_ct = ContentType.objects.get_for_model(models.Event)
        for topic in event_topics:
            models.TopicItem.objects.create(uri=topic,
                                            content_type=event_ct,
                                            object_id=event.id)
        return event

    def clean(self):
        if not self.cleaned_data['title'] and not self.cleaned_data['title_not_announced']:
            raise forms.ValidationError("Either provide title or mark it as not announced")
        return self.cleaned_data


class EventGroupForm(forms.ModelForm):

    class Meta:
        fields = ('title', 'group_type', 'description')
        model = models.EventGroup
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(),
        }


class SpeakerQuickAdd(forms.ModelForm):
    class Meta:
        fields = ('name', 'email_address')
        model = models.Person

    class Media:
        js = ('js/event-element-quick-add.js',)
