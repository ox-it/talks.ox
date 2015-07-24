import logging
from datetime import date, timedelta, datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Event, EventGroup, Person
from talks.events.models import ROLES_SPEAKER, ROLES_HOST, ROLES_ORGANISER
from talks.events.datasources import TOPICS_DATA_SOURCE, DEPARTMENT_DATA_SOURCE, DEPARTMENT_DESCENDANT_DATA_SOURCE

from .forms import BrowseEventsForm

from talks.api.services import events_search

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
    
    nextWeek = today + timedelta(days=7)
    initial_browse_params = '?start_date=' + today.strftime('%Y-%m-%d') + '&to=' + nextWeek.strftime('%Y-%m-%d')

    context = {
        'events': events,
        'event_groups': event_groups,
        'conferences': conferences,
        'group_no_type': group_no_type,
        'series': series,
        'default_collection': None,
        'initial_browse_params' : initial_browse_params
    }
    if request.tuser:
        # Authenticated user
        collection = request.tuser.default_collection
        context['default_collection'] = collection
        context['user_events'] = collection.get_events()
        context['user_event_groups'] = collection.get_event_groups()
    return render(request, 'front.html', context)


def browse_events(request):
    default_form_values = request.GET.copy()
    default_form_values['subdepartments'] = "false"
    default_start_date = None
    if (len(request.GET) == 0):
        default_start_date = 'today'
        default_form_values['start_date'] = date.today().strftime("%Y-%m-%d")
        default_form_values['include_subdepartments'] = True
    elif request.GET.get('subdepartments') and not request.GET.get('include_subdepartments'):
        default_form_values['include_subdepartments'] = False
    
    browse_events_form = BrowseEventsForm(default_form_values)

    count = request.GET.get('count', 20)
    page = request.GET.get('page', 1)

    # used to build a URL fragment that does not
    # contain "page" so that we can... paginate
    args = {'count': count,
            'start_date': request.GET.get('start_date', None),
            'to': request.GET.get('to', None),
            'venue': request.GET.get('venue', None),
            'organising_department': request.GET.get('organising_department', None),
            'subdepartments': request.GET.get('subdepartments', None),
            'seriesid': request.GET.get('seriesid', None),
        }

    
    events = events_search(request, default_start_date)

    paginator = Paginator(events, count)
    try:
        events = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('browse')

    fragment = '&'.join(["{k}={v}".format(k=k, v=v) for k, v in args.iteritems()])

    context = {
        'events': events,
        'fragment': fragment,
        'default_collection': None,
        'browse_events_form' : browse_events_form
        }
    if request.tuser:
        # Authenticated user
        collection = request.tuser.default_collection
        context['default_collection'] = collection
        context['user_events'] = collection.get_events()
        context['user_event_groups'] = collection.get_event_groups()
    return render(request, 'events/browse.html', context)


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
    show_all = request.GET.get('show_all', False)

    if not show_all:
        events = events.filter(start__gte=date.today())

    context = {
        'event_group': group,
        'events': events,
        'organisers': group.organisers.all(),
        'show_all': show_all,
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
    results = DEPARTMENT_DESCENDANT_DATA_SOURCE.get_object_by_id(org_id)
    descendants = results['descendants']
    sub_orgs = descendants
    ids = [o['id'] for o in sub_orgs]
    events = Event.published.filter(department_organiser__in=ids)
    context = {
        'org': org,
        'sub_orgs': sub_orgs,
        'events': events
    }
    return render(request, 'events/department.html', context)
