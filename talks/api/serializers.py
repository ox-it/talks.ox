from rest_framework import serializers

from talks.events.models import Event, Speaker, EventGroup
from talks.users.models import CollectionItem


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('url', 'title', 'start', 'end', 'description')


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
            raise NotImplemented("TODO")
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer.data


class CollectionItemSerializer(serializers.ModelSerializer):
    item = CollectionItemRelatedField()

    class Meta:
        fields = ('id', 'item', 'collection')
        model = CollectionItem
