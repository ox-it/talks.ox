from rest_framework import serializers

from talks.events.models import Event, Speaker, EventGroup
from talks.users.models import CollectionItem


class EventSerializer(serializers.HyperlinkedModelSerializer):
    formatted_date = serializers.CharField(source='formatted_date',
                                           read_only=True)
    formatted_time = serializers.CharField(source='formatted_time',
                                           read_only=True)
    happening_today = serializers.BooleanField(source='happening_today',
                                               read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'url', 'title', 'start', 'end', 'description',
                  'formatted_date', 'formatted_time', 'happening_today')


class EventGroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = EventGroup
        fields = ('id', 'title', 'description')


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ('id', 'name', 'email_address')


class CollectionItemRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `item` generic relationship.
    """

    def to_native(self, value):
        """
        Serialize event instances using a event serializer,
        """
        if isinstance(value, Event):
            serializer = EventSerializer(value)
        elif isinstance(value, EventGroup):
            serializer = EventGroupSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer.data


class CollectionItemSerializer(serializers.ModelSerializer):
    item = CollectionItemRelatedField()

    class Meta:
        fields = ('id', 'item', 'collection')
        model = CollectionItem
