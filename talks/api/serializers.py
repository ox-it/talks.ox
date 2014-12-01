from rest_framework import serializers

from talks.events.models import Event, Person, EventGroup
from talks.users.models import CollectionItem


class ClassNameField(serializers.Field):
    def field_to_native(self, obj, field_name):
        """
        Serialize the object's class name.
        """
        return obj.__class__.__name__


class EventSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)
    formatted_date = serializers.CharField(source='formatted_date',
                                           read_only=True)
    formatted_time = serializers.CharField(source='formatted_time',
                                           read_only=True)
    happening_today = serializers.BooleanField(source='happening_today',
                                               read_only=True)
    class_name = ClassNameField()

    class Meta:
        model = Event
        fields = ('id', 'url', 'title', 'start', 'end', 'description',
                  'formatted_date', 'formatted_time', 'happening_today',
                  'class_name')


class EventGroupSerializer(serializers.ModelSerializer):
    class_name = ClassNameField()
    url = serializers.CharField(source='get_absolute_url',
                                read_only=True)

    class Meta:
        model = EventGroup
        fields = ('id', 'url', 'title', 'description', 'class_name', 'department_organiser')

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name', 'email_address')


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

    def to_native(self, value):
        """
        Serialize event instances using a event serializer,
        """
        serializer = get_item_serializer(value)
        return serializer.data


class CollectionItemSerializer(serializers.ModelSerializer):
    item = CollectionItemRelatedField()

    class Meta:
        fields = ('id', 'item', 'collection')
        model = CollectionItem
