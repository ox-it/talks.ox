import logging
from datetime import datetime
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import operator

from rest_framework import viewsets, status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer
from rest_framework.response import Response

from talks.events.models import Event, EventGroup, Person
from talks.users.authentication import GROUP_EDIT_EVENTS, user_in_group_or_super
from talks.users.models import Collection
from talks.api.serializers import (EventSerializer, PersonSerializer, SpeakerSerializer, EventGroupSerializer, EventGroupWithEventsSerializer, UserSerializer,
                                   CollectionItemSerializer,
                                   get_item_serializer)
from talks.core.renderers import ICalRenderer

logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for events
    """
    renderer_classes = (ICalRenderer, JSONRenderer, JSONPRenderer, XMLRenderer)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'slug'

class EventGroupViewSet(viewsets.ReadOnlyModelViewSet):
    renderer_classes = (ICalRenderer, JSONPRenderer, JSONPRenderer, XMLRenderer)
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupWithEventsSerializer
    lookup_field = 'slug'

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

@api_view(["GET"])
def get_speaker(request, person_slug_list):
    """
    Retrieve details on the supplied speakers, including events which they are speaker at
    :param person_slug_list: a comma-separated list of person slugs
    """
    slugs = person_slug_list.split(",")
    print slugs
    try:
        speakers = Person.objects.filter(slug__in=slugs)
        print speakers
    except ObjectDoesNotExist:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = SpeakerSerializer(speakers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def api_event_search(request):
    """
    Return a list of events based on the query term
    :param query:
        Query which can include the terms
            from=<dd/mm/yy>     -   events starting after this date
            to=<dd/mm/yy>       -   events starting before this date
            speaker=<speaker_slug>  - events where the given speaker is speaking
            venue=<oxpoints_id> - events taking place in the specified buildings (or their children)
            subvenues=<bool=False> - include children of the specified building when searching on venue
            dept=<oxpoints_id> - events with any of organising_departments set as the specified oxpoints entity
            subdepts=<bool=False> - include children of the specified depts when searching on dept
            topic=<topic_uri> - events featuring any of the listed topics as FAST URIs
    :return:
    """
    queries = []

    from_date_param = request.GET.get("from")
    if from_date_param:
        from_date = datetime.strptime(from_date_param, "%d/%m/%y")
    else:
        from_date = datetime.today
    print from_date
    queries.append(Q(start__gt=from_date))

    to_date_param = request.GET.get("to")
    if to_date_param:
        to_date = datetime.strptime(to_date_param, "%d/%m/%y")
        if to_date:
            queries.append(Q(start__lt=to_date))

    # speakers = request.GET.get("speaker").split(',')
    # venues = request.GET.get("venue").split(',')
    # depts = request.GET.get("dept").split(',')
    # topics = request.GET.get("topic").split(',')

    finalQuery = reduce(operator.and_, queries)
    events = Event.objects.filter(finalQuery)
    print events
    serializer = EventSerializer(events, many=True, read_only=True)
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
