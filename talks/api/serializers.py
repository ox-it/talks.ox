from rest_framework import serializers

from talks.events.models import Event


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('url', 'title', 'start', 'end', 'description')
