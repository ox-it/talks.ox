from rest_framework import viewsets

from talks.events.models import Event
from talks.api.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint for events
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
