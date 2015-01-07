import logging
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import viewsets, status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer
from rest_framework.response import Response

from talks.events.models import Event, EventGroup, Person
from talks.users.authentication import GROUP_EDIT_EVENTS, user_in_group_or_super
from talks.users.models import Collection
from talks.api.serializers import (EventSerializer, PersonSerializer, EventGroupSerializer, UserSerializer,
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


class IsSuperuserOrContributor(permissions.BasePermission):
    """
    Only allow superusers or contributors to retrieve email addresses
    """
    def has_permission(self, request, view):
        return user_in_group_or_super(request.user)

# These views are typically used by ajax

@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated, IsSuperuserOrContributor,))
@api_view(["POST"])
def api_create_person(request):
    serializer = PersonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def suggest_person(request):
    query = request.GET.get('q', '')
    persons = Person.objects.suggestions(query)
    serializer = PersonSerializer(persons, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated, IsSuperuserOrContributor,))
def suggest_user(request):
    query = request.GET.get('q', '')
    users = User.objects.filter((Q(is_superuser=True) | Q(groups__name=GROUP_EDIT_EVENTS))
                                & Q(email__startswith=query)).distinct()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_event_group(request, event_group_id):
    try:
        eg = EventGroup.objects.get(id=event_group_id)
    except ObjectDoesNotExist:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = EventGroupSerializer(eg)
    return Response(serializer.data, status=status.HTTP_200_OK)


def item_from_request(request):
    event_slug = request.data.get('event', None)
    group_id = request.data.get('group', None)
    # Our JS doesn't support sending both
    assert not(event_slug and group_id)
    try:
        if event_slug:
            return Event.objects.get(slug=event_slug)
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
