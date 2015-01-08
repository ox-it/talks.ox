from django.contrib.auth.models import User
from rest_framework import serializers

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
        

class EventGroupSerializer(serializers.ModelSerializer):
    class_name = ClassNameField()
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)
    organisers = PersonSerializer(many=True, read_only=True)

    class Meta:

        model = EventGroup
        fields = ('id', 'slug', 'url', 'title', 'description', 'class_name', 'organisers', 'department_organiser')


class EventGroupWithEventsSerializer(serializers.ModelSerializer):
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
