import logging

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer
from rest_framework.response import Response

from talks.events.models import Event, EventGroup, Speaker
from talks.users.models import Collection
from talks.api.serializers import (EventSerializer, SpeakerSerializer,
                                   CollectionItemSerializer,
                                   get_item_serializer)
from talks.core.renderers import ICalRenderer

logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint for events
    """
    renderer_classes = (ICalRenderer, JSONRenderer, JSONPRenderer, XMLRenderer)
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# These views are typically used by ajax

@api_view(["GET"])
def suggest_speaker(request):
    query = request.GET.get('q', '')
    speakers = Speaker.objects.suggestions(query)
    serializer = SpeakerSerializer(speakers, many=True)
    return Response(serializer.data)


# TODO: require auth
@api_view(["POST"])
def create_speaker(request):
    serializer = SpeakerSerializer(data=request.DATA)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def item_from_request(request):
    event_id = request.DATA.get('event', None)
    group_id = request.DATA.get('group', None)
    # Our JS doesn't support sending both
    assert not(event_id and group_id)
    try:
        if event_id:
            return Event.objects.get(id=event_id)
        elif group_id:
            return EventGroup.objects.get(id=group_id)
    except ObjectDoesNotExist:
        logger.warn("Attempt to add thing to event that doesn't exist")


# TODO: require auth
@api_view(["POST"])
def save_item(request, collection_id=None):
    user_collection = request.tuser.default_collection
    item = item_from_request(request)
    if item:
        try:
            item = user_collection.add_item(item)
        except Collection.ItemAlreadyInCollection:
            return Response({'error': "Item already in user collection"},
                            status=status.HTTP_409_CONFLICT)
        serializer = CollectionItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)


# TODO: require auth
@api_view(["POST"])
def remove_item(request, collection_id=None):
    user_collection = request.tuser.default_collection
    item = item_from_request(request)
    deleted = user_collection.remove_item(item)
    if deleted:
        serializer = get_item_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Item not found."},
                        status=status.HTTP_404_NOT_FOUND)
