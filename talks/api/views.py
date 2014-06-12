from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer

from talks.events.models import Event
from talks.api.serializers import EventSerializer
from talks.core.renderers import ICalRenderer


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint for events
    """
    renderer_classes = (ICalRenderer, JSONRenderer, JSONPRenderer, XMLRenderer)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
