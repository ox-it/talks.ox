from django.contrib.auth.models import User
from rest_framework import serializers, pagination
from rest_framework.fields import Field

from talks.events.models import Event, Person, EventGroup
from talks.users.models import CollectionItem


class PersonSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField(method_name='formatted_title')

    def formatted_title(self, obj):
        if obj.bio:
            return obj.name + ', ' + obj.bio
        else:
            return obj.name

    class Meta:
        model = Person
        fields = ('id', 'name', 'bio', 'title', 'web_address')


class ClassNameField(serializers.Field):
    """
    Pass the entire object in the get_attribute method, then render its representation by returning the class name
    """
    def get_attribute(self, obj):
        return obj

    def to_representation(self, value):
        return value.__class__.__name__


class EventSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)
    full_url = serializers.SerializerMethodField()
    formatted_date = serializers.CharField(read_only=True)
    formatted_time = serializers.CharField(read_only=True)
    happening_today = serializers.BooleanField(read_only=True)
    speakers = PersonSerializer(many=True, read_only=True)
    organisers = PersonSerializer(many=True, read_only=True)
    hosts = PersonSerializer(many=True, read_only=True)
    class_name = ClassNameField()
    location = serializers.SerializerMethodField()

    def get_full_url(self, obj):
        if 'request' in self.context:
            request = self.context['request']
            return request.build_absolute_uri(obj.get_absolute_url())
        else:
            return obj.get_absolute_url()

    def get_location(self, event):

        if event.location:
            location = event.api_location
            name = location['name']
            if event.location_details:
                name += " (" + event.location_details + ")"
            location_string = name
            if location.get('address'):
                location_string += ", " + location.get('address')
            return location_string
        elif event.location_details:
            name = event.location_details
            return name
        else:
            return "Venue to be announced"

    class Meta:
        model = Event
        fields = ('slug', 'url', 'title_display', 'start', 'end', 'description',
                  'formatted_date', 'formatted_time', 'speakers', 'organisers', 'hosts', 'happening_today', 'audience', 'api_location',
                  'api_organisation', 'api_topics', 'class_name', 'full_url', 'location', 'organiser_email')


class HALURICharField(Field):
    def to_representation(self, instance):
        return {'href': instance}

    def to_internal_value(self, data):
        return None


class EventLinksSerializer(serializers.ModelSerializer):
    self = serializers.SerializerMethodField()
    talks_page = serializers.SerializerMethodField()

    def get_self(self, obj):
        if 'request' in self.context:
            req = self.context.get('request')
            url = req.build_absolute_uri(obj.get_api_url())
        else:
            url = obj.get_api_url()
        field = HALURICharField()
        return field.to_representation(url)

    def get_talks_page(self, obj):
        if 'request' in self.context:
            req = self.context.get('request')
            url = req.build_absolute_uri(obj.get_absolute_url())
        else:
            url = obj.get_absolute_url()
        field = HALURICharField()
        return field.to_representation(url)

    class Meta:
        model = Event
        fields = ('self', 'talks_page')


class EmbeddedSpeakerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('name', 'bio', 'slug')


class EmbeddedOxpointsSerializer(serializers.Serializer):

    def to_representation(self, instance):
        maps_url = "//maps.ox.ac.uk/#/places/" + instance['id']
        api_url = "//api.m.ox.ac.uk/places/" + instance['id']
        data = {}
        data['name'] = instance['name']
        data['map_link'] = maps_url
        if 'address' in instance:
            data['address'] = instance['address']
        data['_links'] = {'self': {'href': api_url}}
        return data


class EmbeddedTopicSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return {'label': instance['prefLabel'], 'uri': instance['uri']}


class EventEmbedsSerializer(serializers.ModelSerializer):
    speakers = EmbeddedSpeakerSerializer(many=True, read_only=True)
    venue = EmbeddedOxpointsSerializer(source='api_location', read_only=True)
    organising_department = EmbeddedOxpointsSerializer(source='api_organisation', read_only=True)
    topics = EmbeddedTopicSerializer(source='api_topics', many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('speakers', 'venue', 'organising_department', 'topics')


class HALEventSerializer(serializers.ModelSerializer):
    _links = serializers.SerializerMethodField(method_name='get_links')
    _embedded = EventEmbedsSerializer(source='*', read_only=True)

    location_summary = serializers.SerializerMethodField()
    series = serializers.SerializerMethodField()
    organiser_email = serializers.CharField(read_only=True)

    def get_links(self, obj):
        # Return a links serializer, but pass on the context
        serializer = EventLinksSerializer(obj, read_only=True, context=self.context)
        return serializer.data

    def get_location_summary(self, obj):
        api_loc = obj.api_location
        if(api_loc):
            summary = api_loc['name']
            if(obj.location_details):
                summary = summary + ", " + obj.location_details
            if 'address' in api_loc:
                summary = summary + ", " + api_loc['address']
            return summary
        return None

    def get_series(self, obj):
        if obj.group:
            return { 'title': obj.group.title, 'slug': obj.group.slug }
        return None

    class Meta:
        model = Event
        fields = ('_links', 'title_display', 'slug', 'start', 'end', 'formatted_date', 'formatted_time', 'description', 'location_details', 'location_summary', 'series', '_embedded', 'organiser_email')


class SearchResultEmbedsSerializer(serializers.Serializer):
    talks = HALEventSerializer(source='*', many=True, read_only=True)


class HALPreviousPageField(pagination.PreviousPageField):

    def to_representation(self, value):
        if value.has_previous():
            return {'href': super(HALPreviousPageField, self).to_representation(value)}
        return None


class HALNextPageField(pagination.NextPageField):

    def to_representation(self, value):
        if value.has_next():
            return {'href': super(HALNextPageField, self).to_representation(value)}
        return None


class SearchResultLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()
    next = HALNextPageField(source='*')
    prev = HALPreviousPageField(source='*')
    results = None

    def get_self(self, obj):
        req = self.context.get('request')
        link = req.build_absolute_uri()
        return {'href': link}


class HALSearchResultSerializer(serializers.Serializer):
    _links = serializers.SerializerMethodField(method_name='get_links')
    _embedded = serializers.SerializerMethodField(method_name='get_embedded')

    def get_links(self, obj):
        # Return a SearchResultLinksSerializer, but pass the context on by using it a method field
        serializer = SearchResultLinksSerializer(obj, context=self.context)
        return serializer.data

    def get_embedded(self,obj):
        # Pass the context
        serializer = SearchResultEmbedsSerializer(obj, context=self.context)
        return serializer.data

class EventGroupLinksSerializer(serializers.ModelSerializer):
    self = HALURICharField(source='get_api_url', read_only=True)
    talks_page = HALURICharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = EventGroup
        fields = ('self', 'talks_page')


class EventGroupEmbedsSerializer(serializers.ModelSerializer):
    talks = HALEventSerializer(many=True, read_only=True, source='events')

    class Meta:
        model = EventGroup
        fields = ('talks',)


class HALEventGroupSerializer(serializers.ModelSerializer):
    _links = EventGroupLinksSerializer(source='*', read_only=True)
    _embedded = EventGroupEmbedsSerializer(source='*', read_only=True)

    class Meta:
        model = EventGroup
        fields = ('_links', 'title', 'description', 'occurence', '_embedded')


class SpeakerSerializer(serializers.ModelSerializer):
    """
    Serialize a speaker and all the events that they are speaking at
    """
    speaker_events=EventSerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = ('name', 'bio', 'speaker_events')


class EventGroupSerializer(serializers.ModelSerializer):
    class_name = ClassNameField()
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)
    organisers = PersonSerializer(many=True, read_only=True)

    class Meta:

        model = EventGroup
        fields = ('id', 'slug', 'url', 'title', 'description', 'class_name', 'organisers', 'department_organiser')


class EventGroupWithEventsSerializer(serializers.ModelSerializer):
    """
    Serialize an event group and include info on all constitutent events
    """
    events = EventSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'title', 'description', 'department_organiser', 'events')
        model = EventGroup


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


def get_item_serializer(item):
    if isinstance(item, Event):
        return EventSerializer(item)
    elif isinstance(item, EventGroup):
        return EventGroupSerializer(item)
    else:
        raise Exception('Unexpected type of tagged object')


class CollectionItemRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `item` generic relationship.
    """

    def to_representation(self, value):
        """
        Serialize event instances using a event serializer,
        """
        serializer = get_item_serializer(value)
        return serializer.data


class CollectionItemSerializer(serializers.ModelSerializer):
    item = CollectionItemRelatedField(queryset=CollectionItem.objects.all())

    class Meta:
        fields = ('id', 'item', 'collection')
        model = CollectionItem
