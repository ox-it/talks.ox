from django.contrib.auth.models import User
from rest_framework import serializers
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
        fields = ('id', 'name', 'bio', 'title')


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
    formatted_date = serializers.CharField(read_only=True)
    formatted_time = serializers.CharField(read_only=True)
    happening_today = serializers.BooleanField(read_only=True)
    speakers = PersonSerializer(many=True, read_only=True)
    organisers = PersonSerializer(many=True, read_only=True)
    hosts = PersonSerializer(many=True, read_only=True)
    class_name = ClassNameField()

    class Meta:
        model = Event
        fields = ('slug', 'url', 'title', 'start', 'end', 'description',
                  'formatted_date', 'formatted_time', 'speakers', 'organisers', 'hosts', 'happening_today', 'audience', 'api_location',
                  'api_organisation', 'api_topics', 'class_name')


class HALURICharField(Field):
    def to_representation(self, instance):
        return {'href': instance}

    def to_internal_value(self, data):
        return None


class EventLinksSerializer(serializers.ModelSerializer):
    self = HALURICharField(source='get_api_url', read_only=True)
    talks_page = HALURICharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Event
        fields = ('self', 'talks_page')


class HALEventSerializer(serializers.ModelSerializer):
    _links = EventLinksSerializer(source='*', read_only=True)
    formatted_date = serializers.CharField(read_only=True)
    formatted_time = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = ('_links', 'title', 'formatted_date', 'formatted_time', 'description')


class SearchResultEmbedsSerializer(serializers.Serializer):
    talks = HALEventSerializer(source='*', many=True, read_only=True)


class SearchResultLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    def get_self(self, obj):
        req = self.context.get('request')
        link = req.build_absolute_uri()
        return {'href': link}


class HALSearchResultSerializer(serializers.Serializer):
    _links = serializers.SerializerMethodField(method_name='get_links')
    _embedded = SearchResultEmbedsSerializer(source='*')

    def get_links(self, obj):
        # Return a SearchResultLinksSerializer, but pass the context on by using it a method field
        serializer = SearchResultLinksSerializer(obj, many=True, context=self.context)
        return serializer.data


class EventGroupLinksSerializer(serializers.ModelSerializer):
    self = HALURICharField(source='get_api_url', read_only=True)
    talks_page = HALURICharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = EventGroup
        fields = ('self', 'talks_page')


class EventGroupEmbedsSerializer(serializers.ModelSerializer):
    events = HALEventSerializer(many=True, read_only=True)

    class Meta:
        model = EventGroup
        fields = ('events',)


class HALEventGroupSerializer(serializers.ModelSerializer):
    _links = EventGroupLinksSerializer(source='*', read_only=True)
    _embedded = EventGroupEmbedsSerializer(source='*', read_only=True)

    class Meta:
        model = EventGroup
        fields = ('_links', 'title', 'description', 'occurence', '_embedded')


        fields = ('_links', 'title', 'slug', 'description', 'occurence', '_embedded')
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
