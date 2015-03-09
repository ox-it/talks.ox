import logging
from datetime import date, timedelta

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Event, EventGroup, Person
from talks.events.models import ROLES_SPEAKER, ROLES_HOST, ROLES_ORGANISER
from talks.events.datasources import TOPICS_DATA_SOURCE, DEPARTMENT_DATA_SOURCE, DEPARTMENT_DESCENDANT_DATA_SOURCE

logger = logging.getLogger(__name__)


def homepage(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    events = Event.published.filter(start__gte=today,
                                    start__lt=tomorrow).order_by('start')
    event_groups = EventGroup.objects.for_events(events)
    conferences = filter(lambda eg: eg.group_type == EventGroup.CONFERENCE,
                         event_groups)
    series = filter(lambda eg: eg.group_type == EventGroup.SEMINAR,
                    event_groups)
    group_no_type = filter(lambda eg: not eg.group_type,
                           event_groups)
    context = {
        'events': events,
        'event_groups': event_groups,
        'conferences': conferences,
        'group_no_type': group_no_type,
        'series': series,
        'default_collection': None,
    }
    if request.tuser:
        # Authenticated user
        collection = request.tuser.default_collection
        context['default_collection'] = collection
        context['user_events'] = collection.get_events()
        context['user_event_groups'] = collection.get_event_groups()
    return render(request, 'front.html', context)


def upcoming_events(request):
    today = date.today()
    events = Event.published.filter(start__gte=today).order_by('start')
    return _events_list(request, events)


def events_for_year(request, year):
    events = Event.published.filter(start__year=year)
    return _events_list(request, events)


def events_for_month(request, year, month):
    events = Event.published.filter(start__year=year,
                                    start__month=month)
    return _events_list(request, events)


def events_for_day(request, year, month, day):
    events = Event.published.filter(start__year=year,
                                    start__month=month,
                                    start__day=day)
    return _events_list(request, events)


def _events_list(request, events):
    context = {'events': events}
    return render(request, 'events/events.html', context)


def show_event(request, event_slug):
    try:
        # TODO depending if user is admin or not,
        # we should use Event.published here...
        ev = Event.objects.select_related(
            'speakers',
            'hosts',
            'organisers',
            'location',
            'group',
            'department_organiser').get(slug=event_slug)
    except Event.DoesNotExist:
        raise Http404
    context = {
        'event': ev,
        'url': request.build_absolute_uri(reverse('show-event', args=[ev.slug])),
        'location': ev.api_location,
        'speakers': ev.speakers.all(),
        'hosts': ev.hosts.all(),
        'organisers': ev.organisers.all(),
    }
    return render(request, 'events/event.html', context)


def list_event_groups(request):
    object_list = EventGroup.objects.all()
    context = {
        'object_list': object_list,
    }
    return render(request, "events/event_group_list.html", context)


def show_event_group(request, event_group_slug):
    group = get_object_or_404(EventGroup, slug=event_group_slug)
    events = group.events.order_by('start')
    context = {
        'event_group': group,
        'events': events,
        'organisers': group.organisers.all(),
    }
    return render(request, 'events/event-group.html', context)


def show_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)

    if request.user.has_perm('events.change_person'):
        events = Event.objects.order_by('start')
    else:
        events = Event.published.order_by('start')

    host_events = events.filter(personevent__role=ROLES_HOST, personevent__person__slug=person.slug)
    speaker_events = events.filter(personevent__role=ROLES_SPEAKER, personevent__person__slug=person.slug)
    organiser_events = events.filter(personevent__role=ROLES_ORGANISER, personevent__person__slug=person.slug)

    context = {
        'person': person,
        'host_events': host_events,
        'speaker_events': speaker_events,
        'organiser_events': organiser_events,
    }
    return render(request, 'events/person.html', context)


def show_topic(request):
    topic_uri = request.GET.get('uri')
    api_topic = TOPICS_DATA_SOURCE.get_object_by_id(topic_uri)
    events = Event.published.filter(topics__uri=topic_uri)
    context = {
        'topic': api_topic,
        'events': events
    }
    return render(request, 'events/topic.html', context)


def show_department_organiser(request, org_id):
    org = DEPARTMENT_DATA_SOURCE.get_object_by_id(org_id)
    events = Event.published.filter(department_organiser=org_id)
    context = {
        'org': org,
        'events': events
    }
    return render(request, 'events/department.html', context)


def show_department_descendant(request, org_id):
    org = DEPARTMENT_DATA_SOURCE.get_object_by_id(org_id)
    print org
    print "GETTING DEPT DESCENDANTS"
    results = DEPARTMENT_DESCENDANT_DATA_SOURCE.get_object_by_id(org_id)
    descendants = results['descendants']
    sub_orgs = descendants
    print sub_orgs
    ids = [o['id'] for o in sub_orgs]
    events = Event.published.filter(department_organiser__in=ids)
    context = {
        'org': org,
        'sub_orgs': sub_orgs,
        'events': events
    }
    return render(request, 'events/department.html', context)
