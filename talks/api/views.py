import logging
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import operator
from django.http.response import HttpResponse

from rest_framework import viewsets, status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer
from rest_framework.response import Response

from talks.events.models import Event, EventGroup, Person, ROLES_SPEAKER, TopicItem
from talks.users.authentication import GROUP_EDIT_EVENTS, user_in_group_or_super
from talks.users.models import Collection
from talks.api.serializers import (EventSerializer, PersonSerializer, SpeakerSerializer, EventGroupSerializer, EventGroupWithEventsSerializer, UserSerializer,
                                   CollectionItemSerializer,
                                   get_item_serializer, HALEventSerializer, HALEventGroupSerializer,
                                   HALSearchResultSerializer)
from talks.core.renderers import ICalRenderer

logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for events
    """
    renderer_classes = (ICalRenderer, JSONRenderer, JSONPRenderer, XMLRenderer)
    queryset = Event.objects.all()
    serializer_class = HALEventSerializer
    lookup_field = 'slug'


class EventGroupViewSet(viewsets.ReadOnlyModelViewSet):
    renderer_classes = (ICalRenderer, JSONRenderer, JSONPRenderer, XMLRenderer)
    queryset = EventGroup.objects.all()
    serializer_class = HALEventGroupSerializer
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
    """
    Used via ajax to retrieve group details when changing selection
    """
    try:
        eg = EventGroup.objects.get(id=event_group_id)
    except ObjectDoesNotExist:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = EventGroupSerializer(eg)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def api_event_search(request):
    """
    Return a list of events based on the query term
    """
    queries = []

    from_date = parse_date(request.GET.get("from"))
    if not from_date:
        raise ParseError(detail="'from' parameter is mandatory. Supply either 'today' or a date in form 'dd/mm/yy'.")
    else:
        queries.append(Q(start__gt=from_date))

    to_date = parse_date(request.GET.get("to"))
    if to_date:
        queries.append(Q(start__lt=to_date))

    speakers = request.GET.getlist("speaker")
    if speakers:
        queries.append(Q(personevent__role=ROLES_SPEAKER, personevent__person__slug__in=speakers))

    venues = request.GET.getlist("venue")
    if venues:
        queries.append(Q(location__in=venues))

    depts = request.GET.getlist("organising_department")
    if depts:
        queries.append(Q(department_organiser__in=depts))

    topics = request.GET.getlist("topic")
    if topics:
        queries.append(Q(topics__uri__in=topics))

    final_query = reduce(operator.and_, queries)
    events = Event.published.filter(final_query)
    serializer = HALSearchResultSerializer(events, read_only=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


def parse_date(date_param):
    """
    Parse the date string parameter
    :param date_param:
        Either a keyword:
            'today', 'tomorrow'
        or a string in the format 'dd/mm/yy'
    :return:
        datetime object
    """
    if not date_param:
        return None
    elif date_param == "today":
        from_date = datetime.today().date()
    elif date_param == "tomorrow":
        from_date = datetime.today().date() + timedelta(1)
    else:
        try:
            from_date = datetime.strptime(date_param, "%d/%m/%y")
        except Exception as e:
            # catch the exception and raise an API exception instead, which the user will see
            raise ParseError(e.message);
    return from_date


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
