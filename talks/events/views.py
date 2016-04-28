import logging
from datetime import date, timedelta

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Event, EventGroup, Person, TopicItem
from talks.events.models import ROLES_SPEAKER, ROLES_HOST, ROLES_ORGANISER
from talks.events.datasources import TOPICS_DATA_SOURCE, DEPARTMENT_DATA_SOURCE, DEPARTMENT_DESCENDANT_DATA_SOURCE
from talks.users.models import COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER
from .forms import BrowseEventsForm
from talks.api.services import events_search

logger = logging.getLogger(__name__)


def homepage(request):

    HOMEPAGE_YOUR_TALKS_RESULTS_LIMIT = 5

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
        'series': series
    }
    if request.tuser:
        # Authenticated user
        collections = request.tuser.collections.all()
        if collections:
            user_events = collections[0].get_all_events()
            for collection in collections[1:]:
                user_events = user_events | collection.get_all_events()
            context['collections'] = collections
            user_events = user_events.filter(start__gte=today)
            if (user_events.count() > HOMEPAGE_YOUR_TALKS_RESULTS_LIMIT):
                context['user_events_more_link'] = True
            context['user_events'] = user_events[:HOMEPAGE_YOUR_TALKS_RESULTS_LIMIT]

    return render(request, 'front.html', context)


def browse_events(request):
    modified_request_parameters = request.GET.copy()
    modified_request_parameters['subdepartments'] = "false"
    if (len(request.GET) == 0) or (len(request.GET) == 1) and request.GET.get('limit_to_collections'):
        today = date.today()
        defaultEndDate = date.today() + timedelta(days=7*8)
        modified_request_parameters['start_date'] = today.strftime("%Y-%m-%d")
        if len(request.GET) == 0:
            modified_request_parameters['to'] = defaultEndDate.strftime("%Y-%m-%d")
        modified_request_parameters['include_subdepartments'] = True
        modified_request_parameters['subdepartments'] = 'true'
    elif request.GET.get('include_subdepartments'):
        modified_request_parameters['include_subdepartments'] = True
        modified_request_parameters['subdepartments'] = 'true'
    else:
        modified_request_parameters['include_subdepartments'] = False
        modified_request_parameters['subdepartments'] = 'false'

    browse_events_form = BrowseEventsForm(modified_request_parameters)

    count = request.GET.get('count', 20)
    page = request.GET.get('page', 1)

    if request.GET.get('limit_to_collections'):
        modified_request_parameters['limit_to_collections'] = request.tuser.collections.all()

    # used to build a URL fragment that does not
    # contain "page" so that we can... paginate
    args = {'count': count}
    for param in ('start_date', 'to', 'venue', 'organising_department', 'include_subdepartments', 'seriesid', 'limit_to_collections'):
        if modified_request_parameters.get(param):
            args[param] = modified_request_parameters.get(param)
    
    if not modified_request_parameters['start_date']:
        return redirect(reverse('browse_events'))

    events = events_search(modified_request_parameters)
        
    paginator = Paginator(events, count)
    try:
        events = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect(reverse('browse_events'))

    grouped_events = {}
    event_dates = []
    for group_event in events:
        key = group_event.start.date()
        if key not in grouped_events:
            grouped_events[key] = []
            event_dates.append(key)
        grouped_events[key].append(group_event)
    
    result_events = []
    for event_date in event_dates:
        result_events.append({"start_date":event_date, "gr_events":grouped_events[event_date]})

    fragment = '&'.join(["{k}={v}".format(k=k, v=v) for k, v in args.iteritems()])

    context = {
        'events': events,
        'result_events': result_events,
        'fragment': fragment,
        'browse_events_form': browse_events_form,
        'start_date': modified_request_parameters.get('start_date'),
        'end_date': modified_request_parameters.get('to'),
        }
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
        'editors': ev.editor_set.all(),
    }
    if request.tuser:
        context['editable_collections'] = request.tuser.collections.filter(talksusercollection__role__in=[COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR]).distinct()

    if request.GET.get('format') == 'txt':
        return render(request, 'events/event.txt.html', context)
    else:
        return render(request, 'events/event.html', context)


def list_event_groups(request):
            
    modified_request_parameters = request.GET.copy()
    if request.POST.get('seriesslug'):
        return redirect('show-event-group', request.POST.get('seriesslug'))
        
    browse_events_form = BrowseEventsForm(modified_request_parameters)
    
    object_list = EventGroup.objects.all().order_by('title')
    context = {
        'object_list': object_list,
        'browse_events_form': browse_events_form, 
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

    if request.tuser:
        context['editable_collections'] = request.tuser.collections.filter(talksusercollection__role__in=[COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR]).distinct()

    if request.GET.get('format') == 'txt':
        return render(request, 'events/event-group.txt.html', context)
    else:
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
    if request.GET.get('format') == 'txt':
        return render(request, 'events/person.txt.html', context)
    else:
        return render(request, 'events/person.html', context)


def show_topic(request):
    topic_uri = request.GET.get('uri')
    api_topic = TOPICS_DATA_SOURCE.get_object_by_id(topic_uri)
    events = Event.published.filter(topics__uri=topic_uri)
    context = {
        'topic': api_topic,
        'events': events
    }
    if request.GET.get('format') == 'txt':
        return render(request, 'events/topic.txt.html', context)
    else:
        return render(request, 'events/topic.html', context)

def list_topics(request):
    topics = TopicItem.objects.distinct()
    topics_results = []
    
    for topic in topics.all():
        events = Event.published.filter(topics__uri=topic.uri)
        if(len(events)>0):
            api_topic = TOPICS_DATA_SOURCE.get_object_by_id(topic.uri)
            if api_topic not in topics_results:
                topics_results.append(api_topic)
    
    context = {
        'topics': topics_results,
    }
    
    return render(request, 'events/topic_list.html', context)

def show_department_organiser(request, org_id):
    org = DEPARTMENT_DATA_SOURCE.get_object_by_id(org_id)
    events = Event.published.filter(department_organiser=org_id).order_by('start')

    show_all = request.GET.get('show_all', False)
    if not show_all:
        events = events.filter(start__gte=date.today())

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
    ids.append(results['id'])  # Include self
    events = Event.published.filter(department_organiser__in=ids).order_by('start')

    show_all = request.GET.get('show_all', False)
    if not show_all:
        events = events.filter(start__gte=date.today())

    if org['_links'].has_key('parent'):
        parent_href = org['_links']['parent'][0]['href']
        parent_id = parent_href[parent_href.find("oxpoints"):]
        parent = DEPARTMENT_DATA_SOURCE.get_object_by_id(parent_id)
    else:
        parent = None

    context = {
        'org': org,
        'sub_orgs': sub_orgs,
        'events': events,
        'parent': parent,
        'show_all': show_all,
        'todays_date': date.today().strftime("%Y-%m-%d"),
    }
    if request.GET.get('format') == 'txt':
        return render(request, 'events/department.txt.html', context)
    else:
        return render(request, 'events/department.html', context)
