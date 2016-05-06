import logging
import functools
from datetime import date, timedelta, datetime

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Event, EventGroup, Person, TopicItem
from talks.events.models import ROLES_SPEAKER, ROLES_HOST, ROLES_ORGANISER
from talks.events.datasources import TOPICS_DATA_SOURCE, DEPARTMENT_DATA_SOURCE, DEPARTMENT_DESCENDANT_DATA_SOURCE
from talks.users.models import COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER
from .forms import BrowseEventsForm, BrowseSeriesForm
from talks.api.services import events_search
from talks.api_ox.api import OxfordDateResource

logger = logging.getLogger(__name__)


def homepage(request):

    HOMEPAGE_YOUR_TALKS_RESULTS_LIMIT = 5

    today = date.today()
    tomorrow = today + timedelta(days=1)
    events = Event.objects.filter(start__gte=today,
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
        modified_request_parameters['start_date'] = today.strftime("%d/%m/%Y")
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

    grouped_events = group_events(events)

    fragment = '&'.join(["{k}={v}".format(k=k, v=v) for k, v in args.iteritems()])

    old_query = request.META['QUERY_STRING']
    dates_start = old_query.find("start_date=")
    dates_end = dates_start + 35
    today = date.today()
    offset_Sunday = (6 - today.weekday()) % 7 # weekday(): Monday=0 .... Sunday=6
    tab_dates = [
        {
            'label': 'All',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today) + old_query[dates_end:],
            'active': False
        }, {
            'label': 'Today',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today) + '&to=' + str(today) + old_query[dates_end:],
            'active': False
        }, {
            'label': 'Tomorrow',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today+timedelta(days=1)) + '&to=' + str(today+timedelta(days=1)) + old_query[dates_end:],
            'active': False
        }, {
            'label': 'This week',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today) + '&to=' + str(today+timedelta(days=offset_Sunday)) + old_query[dates_end:],
            'active': False
        }, {
            'label': 'Next week',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today+timedelta(days=offset_Sunday+1)) + '&to=' + str(today+timedelta(days=offset_Sunday+7)) + old_query[dates_end:],
            'active': False
        }, {
            'label': 'Next 30 days',
            'href': 'browse?' + old_query[:dates_start] + 'start_date='+ str(today) + '&to=' + str(today+timedelta(days=30)) + old_query[dates_end:],
            'active': False
        }
   ]

    if not old_query:
        tab_dates[0]['active'] = True
    else:
        for tab in tab_dates:
            if tab['href'] == 'browse?' + old_query:
                tab['active'] = True
                
    date_continued_previous = False
    if int(page) != 1:
        # if the date of the first talk of the current page is the same with that of the last talk of the previous page
        if list(events)[0].start.date()==list(paginator.page(int(page)-1))[-1].start.date():
            date_continued_previous = True

    date_continued_next = False
    if paginator.num_pages != int(page):
        # if the date of the last talk of the current page is the same with that of the first talk of the next page
        if list(events)[-1].start.date()==list(paginator.page(int(page)+1))[0].start.date():
            date_continued_next = True
        
    context = {
        'events': events,
        'grouped_events': grouped_events,
        'fragment': fragment,
        'browse_events_form': browse_events_form,
        'start_date': modified_request_parameters.get('start_date'),
        'end_date': modified_request_parameters.get('to'),
        'tab_dates': tab_dates,
        'date_continued_previous': date_continued_previous,
        'date_continued_next': date_continued_next,
        }
    return render(request, 'events/browse.html', context)

def group_events (events):
    grouped_events = {}
    event_dates = []
    for group_event in events:
        hours = datetime.strftime(group_event.start, '%I')
        minutes = datetime.strftime(group_event.start, ':%M')
        if minutes==":00":
            minutes = ""
        ampm = datetime.strftime(group_event.start, '%p')
        group_event.display_time = str(int(hours))+minutes+ampm.lower()
        # if there is no oxford_date field, events are search results
        # we need to call date_to_oxford_date to create the oxford date
        if not group_event.oxford_date:
            group_event.oxford_date = date_to_oxford_date(group_event.start)

        comps = group_event.oxford_date.components
        key = comps['day_name']+ " " +str(comps['day_number'])+ " " +comps['month_long']+ " "
        key+= str(comps['year'])+ " ("+ str(comps['week']) + comps['ordinal']+ " Week, " +comps['term_long']+ " Term)"
        
        if key not in grouped_events:
            grouped_events[key] = []
            event_dates.append(key)
        grouped_events[key].append(group_event)

    result_events = []
    for event_date in event_dates:
        result_events.append({"start_date":event_date, "gr_events":grouped_events[event_date]})

    return result_events

def date_to_oxford_date(date_str):
    func = functools.partial(OxfordDateResource.from_date, date_str)
    try:
        res = func()
        return res
    except ApiException:
        logger.warn('Unable to reach API', exc_info=True)
        return None


def upcoming_events(request):
    today = date.today()
    events = Event.objects.filter(start__gte=today).order_by('start')
    return _events_list(request, events)


def events_for_year(request, year):
    events = Event.objects.filter(start__year=year)
    return _events_list(request, events)


def events_for_month(request, year, month):
    events = Event.objects.filter(start__year=year,
                                    start__month=month)
    return _events_list(request, events)


def events_for_day(request, year, month, day):
    events = Event.objects.filter(start__year=year,
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

    browse_series_form = BrowseSeriesForm(modified_request_parameters)

    object_list = EventGroup.objects.all().order_by('title')
    context = {
        'object_list': object_list,
        'browse_events_form': browse_series_form,
    }
    return render(request, "events/event_group_list.html", context)


def show_event_group(request, event_group_slug):
    group = get_object_or_404(EventGroup, slug=event_group_slug)
    events = group.events.order_by('start')
    show_all = request.GET.get('show_all', False)

    if not show_all:
        events = events.filter(start__gte=date.today())

    grouped_events = group_events(events)

    context = {
        'event_group': group,
        'events': events,
        'grouped_events': grouped_events,
        'organisers': group.organisers.all(),
        'show_all': show_all,
        'editors': group.editor_set.all(),
    }

    if request.tuser:
        context['editable_collections'] = request.tuser.collections.filter(talksusercollection__role__in=[COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR]).distinct()

    if request.GET.get('format') == 'txt':
        return render(request, 'events/event-group.txt.html', context)
    else:
        return render(request, 'events/event-group.html', context)

def show_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)

    events = Event.objects.order_by('start')

    host_events = events.filter(personevent__role=ROLES_HOST, personevent__person__slug=person.slug)
    speaker_events = events.filter(personevent__role=ROLES_SPEAKER, personevent__person__slug=person.slug)
    organiser_events = events.filter(personevent__role=ROLES_ORGANISER, personevent__person__slug=person.slug)
    grouped_host_events = group_events(host_events)
    grouped_speaker_events = group_events(speaker_events)
    grouped_organiser_events = group_events(organiser_events)

    context = {
        'person': person,
        'host_events': host_events,
        'speaker_events': speaker_events,
        'organiser_events': organiser_events,
        'grouped_host_events': grouped_host_events,
        'grouped_speaker_events': grouped_speaker_events,
        'grouped_organiser_events': grouped_organiser_events,
    }
    if request.GET.get('format') == 'txt':
        return render(request, 'events/person.txt.html', context)
    else:
        return render(request, 'events/person.html', context)


def show_topic(request):
    topic_uri = request.GET.get('uri')
    api_topic = TOPICS_DATA_SOURCE.get_object_by_id(topic_uri)
    events = Event.objects.filter(topics__uri=topic_uri)

    #RB 3/5/16 get filtered by current talks in topic
    show_all = request.GET.get('show_all', False)
    if not show_all:
        events = events.filter(start__gte=date.today())

    grouped_events = group_events(events)
    context = {
        'grouped_events': grouped_events,
        'topic': api_topic,
        'events': events,
        'show_all': show_all#RB 3/5/16 get filtered by current talks in topic
    }
    if request.GET.get('format') == 'txt':
        return render(request, 'events/topic.txt.html', context)
    else:
        return render(request, 'events/topic.html', context)

def list_topics(request):
    topics = TopicItem.objects.distinct()
    topics_results = []

    for topic in topics.all():
        events = Event.objects.filter(topics__uri=topic.uri)
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
    events = Event.objects.filter(department_organiser=org_id).order_by('start')

    show_all = request.GET.get('show_all', False)
    if not show_all:
        events = events.filter(start__gte=date.today())


    context = {
        'org': org,
        'events': events,
        'department': org_id
    }

    if request.tuser:
        context['editable_collections'] = request.tuser.collections.filter(talksusercollection__role__in=[COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR]).distinct()

    return render(request, 'events/department.html', context)


def show_department_descendant(request, org_id):
    org = DEPARTMENT_DATA_SOURCE.get_object_by_id(org_id)
    try:
        results = DEPARTMENT_DESCENDANT_DATA_SOURCE.get_object_by_id(org_id)
        descendants = results['descendants']
        sub_orgs = descendants
        ids = [o['id'] for o in sub_orgs]
        ids.append(results['id'])  # Include self
        events = Event.objects.filter(department_organiser__in=ids).order_by('start')
    except Exception:
        print "Error retrieving sub-departments, only showing department"
        events = Event.objects.filter(department_organiser=org).order_by('start')
        sub_orgs = []

    show_all = request.GET.get('show_all', False)
    if not show_all:
        events = events.filter(start__gte=date.today())

    grouped_events = group_events(events)

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
        'grouped_events': grouped_events,
        'parent': parent,
        'show_all': show_all,
        'todays_date': date.today().strftime("%Y-%m-%d"),
        'department': org_id
    }

    if request.tuser:
        context['editable_collections'] = request.tuser.collections.filter(talksusercollection__role__in=[COLLECTION_ROLES_OWNER, COLLECTION_ROLES_EDITOR]).distinct()


    if request.GET.get('format') == 'txt':
        return render(request, 'events/department.txt.html', context)
    else:
        return render(request, 'events/department.html', context)
