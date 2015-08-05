import logging
from datetime import date

from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http.response import Http404

from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from talks.events.models import Event, EventGroup, Person
from talks.users.authentication import GROUP_EDIT_EVENTS, user_in_group_or_super
from talks.users.models import Collection, TalksUserCollection, COLLECTION_ROLES_READER
from talks.api.serializers import (PersonSerializer, EventGroupSerializer, UserSerializer,
                                   CollectionItemSerializer, TalksUserCollectionSerializer, get_item_serializer, HALEventSerializer,
                                   HALEventGroupSerializer, HALSearchResultSerializer, EventSerializer)
from talks.api.services import events_search, get_event_by_slug, get_eventgroup_by_slug
from talks.core.renderers import ICalRenderer

logger = logging.getLogger(__name__)


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
def api_event_group(request, event_group_slug):
    """Serialise an EventGroup
    :param request: DRF request object
    :param event_group_slug: event group slug
    :return: DRF response object
    """
    eg = get_eventgroup_by_slug(event_group_slug)
    if not eg:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = HALEventGroupSerializer(eg)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@renderer_classes((ICalRenderer,))
def api_event_group_ics(request, event_group_slug):
    """Get events from an eventgroup to be displayed
    as an iCal feed
    """
    eg = get_eventgroup_by_slug(event_group_slug)
    if not eg:
        return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(eg.events, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def suggest_event_group(request):
    """Get event group titles for typeahead searching
    """
    query = request.GET.get('q', '')
    series = EventGroup.objects.filter(Q(title__startswith=query)).distinct()
    serializer = EventGroupSerializer(series, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def api_event_search_hal(request):
    """
    Return a list of events using the HAL serialisation,
    based on the query terms
    """
    events = events_search(request.GET)

    count = request.GET.get('count', 20)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(events, count)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    serializer = HALSearchResultSerializer(page, read_only=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@renderer_classes((ICalRenderer,))
def api_event_search_ics(request):
    """
    Return a list of events using the iCAl serialisation,
    based on the query terms
    """
    events = events_search(request.GET)
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data,
                    status=status.HTTP_200_OK, content_type=ICalRenderer.media_type)


@api_view(["GET"])
def api_event_get(request, slug):
    event = get_event_by_slug(slug)
    if not event:
        raise Http404
    serializer = HALEventSerializer(event, read_only=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@renderer_classes((ICalRenderer,))
def api_event_get_ics(request, slug):
    event = get_event_by_slug(slug)
    if not event:
        raise Http404
    serializer = EventSerializer(event)
    return Response(serializer.data,
                    status=status.HTTP_200_OK, content_type=ICalRenderer.media_type)


def item_from_request(request):
    event_slug = request.data.get('event', None)
    group_slug = request.data.get('group', None)
    # Our JS doesn't support sending both
    assert not(event_slug and group_slug)
    try:
        if event_slug:
            return Event.objects.get(slug=event_slug)
        elif group_slug:
            return EventGroup.objects.get(slug=group_slug)
    except ObjectDoesNotExist:
        logger.warn("Attempt to add event that doesn't exist to collection")


def collection_from_request(request):
    collection_slug = request.data.get('collection', None)
    try:
        if collection_slug:
            return Collection.objects.get(slug=collection_slug)
    except ObjectDoesNotExist:
        logger.warn("Attempt to add event to collection that doesn't exist")


# TODO: require auth
@api_view(["POST"])
def save_item(request):
    item = item_from_request(request)
    collection = collection_from_request(request)
    if item and collection:
        try:
            item = collection.add_item(item)
        except Collection.ItemAlreadyInCollection:
            return Response({'error': "Item already in user collection"},
                            status=status.HTTP_409_CONFLICT)
        serializer = CollectionItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        if item:
            return Response({'error': "Collection not found"},
                        status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': "Item not found"},
                        status=status.HTTP_404_NOT_FOUND)


# TODO: require auth
@api_view(["POST"])
def remove_item(request):
    collection = collection_from_request(request)
    item = item_from_request(request)
    deleted = collection.remove_item(item)
    if deleted:
        serializer = get_item_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Item not found."},
                        status=status.HTTP_404_NOT_FOUND)

# TODO: require auth
@api_view(["POST"])
def subscribe_to_list(request):
    collection = collection_from_request(request)
    if collection:
        if collection.public:
            TalksUserCollection.objects.get_or_create(user=request.tuser,
                                                    collection=collection,
                                                    role=COLLECTION_ROLES_READER)
            try:
                usercollection = TalksUserCollection.objects.get(user=request.tuser,
                                                    collection=collection,
                                                    role=COLLECTION_ROLES_READER)
                serializer = TalksUserCollectionSerializer(usercollection)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'error': "Failed to subscribe to collection"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': "Collection is not public"},
                            status=status.HTTP_403_FORBIDDEN)

    else:
        return Response({'error': "Collection not found"},
                        status=status.HTTP_404_NOT_FOUND)


# TODO: require auth
@api_view(["POST"])
def unsubscribe_from_list(request):
    collection = collection_from_request(request)
    try:
        usercollection = TalksUserCollection.objects.get(user=request.tuser,
                                            collection=collection,
                                            role=COLLECTION_ROLES_READER)
        deleted = usercollection.delete()
        serializer = TalksUserCollectionSerializer(usercollection)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'error': "Failed to unsubscribe from collection"},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@renderer_classes((ICalRenderer,))
def api_collection_ics(request, collection_slug):
    """Get events and event groups from a collection to be displayed
    as an iCal feed
    """
    try:
        collection = Collection.objects.get(slug=collection_slug)
        today = date.today()
        events = collection.get_all_events().filter(start__gte=today)

        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'error': "Collection not found"},
                        status=status.HTTP_404_NOT_FOUND)

