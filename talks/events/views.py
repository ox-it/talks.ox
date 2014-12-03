import logging
import json

from datetime import date, timedelta
from functools import partial
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Event, EventGroup, Person
from .forms import EventForm, EventGroupForm, SpeakerQuickAdd
from talks.api import serializers
from talks.events.forms import PersonForm

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
    }
    return render(request, 'events/event.html', context)

@login_required
@permission_required('events.change_event', raise_exception=PermissionDenied)
def edit_event(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    if not event.user_can_edit(request.user):
        raise PermissionDenied
    form = EventForm(request.POST or None, instance=event, prefix='event')
    context = {
        'event': event,
        'event_form': form,
        'speaker_form': SpeakerQuickAdd(),
        'event_edition': True
    }
    if request.method == 'POST':
        if form.is_valid():
            event = form.save()
            messages.success(request, "Event was updated")
            return redirect(event.get_absolute_url())
        else:
            messages.warning(request, "Please correct errors below")
    return render(request, "events/event_form.html", context)

@login_required
@permission_required("events.add_event", raise_exception=PermissionDenied)
def create_event(request, group_slug=None):
    initial = None
    event_group = None
    logger.debug("group_id:%s", group_slug)
    if group_slug:
        event_group = get_object_or_404(EventGroup, slug=group_slug)
        initial = {
            'group': event_group,
        }

    PrefixedEventForm = partial(EventForm, prefix='event', initial=initial)

    if request.method == 'POST':
        context = {
            'event_form': PrefixedEventForm(request.POST),
            'speaker_form': SpeakerQuickAdd(),
        }
        forms_valid = context['event_form'].is_valid()
        if forms_valid:
            logging.debug("form is valid")
            event = context['event_form'].save()
            event.editor_set.add(request.user)
            event.save()
            messages.success(request, "New event has been created")
            if 'another' in request.POST:
                if event_group:
                    logger.debug("redirecting to create-event-in-group")
                    # Adding more events, redirect to the create event in existing group form
                    return HttpResponseRedirect(reverse('create-event-in-group', args=(event_group.slug,)))
                else:
                    logger.debug("redirecting to create-event")
                    return HttpResponseRedirect(reverse('create-event'))
            else:
                return HttpResponseRedirect(reverse('show-event', args=(event.slug,)))
        else:
            logging.debug("form is NOT valid")
            messages.warning(request, "Please correct errors below")
    else:
        context = {
            'event_form': PrefixedEventForm(),
            'speaker_form': SpeakerQuickAdd(),
            'event_edition': False
        }
    return render(request, 'events/event_form.html', context)


@login_required
@permission_required('events.delete_event', raise_exception=PermissionDenied)
def delete_event(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    if not event.user_can_edit(request.user):
        raise PermissionDenied
    context = {
        'event': event,
    }
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event has been successfully deleted")
        return redirect('contributors-events')
    return render(request, "events/delete_event.html", context)


def list_event_groups(request):
    object_list = EventGroup.objects.all()
    context = {
        'object_list': object_list,
    }
    return render(request, "events/event_group_list.html", context)


def show_event_group(request, event_group_slug):
    group = get_object_or_404(EventGroup, slug=event_group_slug)
    context = {
        'event_group': group,
    }
    return render(request, 'events/event-group.html', context)

@login_required
@permission_required('events.change_eventgroup', raise_exception=PermissionDenied)
def edit_event_group(request, event_group_slug):
    group = get_object_or_404(EventGroup, slug=event_group_slug)
    form = EventGroupForm(request.POST or None, instance=group)
    if request.method == 'POST':
        logging.debug("incoming post: %s", request.POST)
        if form.is_valid():
            event_group = form.save()
            messages.success(request, "Event group was updated")
            return redirect(event_group.get_absolute_url())
        else:
            messages.warning(request, "Please correct errors below")
    context = {
        'form': form,
        'event_group': group,
    }
    return render(request, 'events/event_group_form.html', context)

@login_required
@permission_required('events.add_eventgroup', raise_exception=PermissionDenied)
def create_event_group(request):
    form = EventGroupForm(request.POST or None)
    is_modal = request.GET.get('modal')
    status_code = 200
    if request.method == 'POST':
        if form.is_valid():
            event_group = form.save()
            if is_modal:
                response = json.dumps(serializers.EventGroupSerializer(event_group).data)
                return HttpResponse(response, status=201, content_type='application/json')
            messages.success(request, "Event group was created")
            return redirect(event_group.get_absolute_url())
        else:
            status_code = 400
            messages.warning(request, "Please correct errors below")

    context = {
        'form': form,
        'modal_title': "Add a new event group",
    }

    if is_modal:
        return render(request, 'modal_form.html', context, status=status_code)
    else:
        return render(request, 'events/event_group_form.html', context, status=status_code)

def contributors_home(request):
    return HttpResponseRedirect(reverse('contributors-events'))


@login_required()
@permission_required('events.add_person', raise_exception=PermissionDenied)
def create_person(request):
    form = PersonForm(request.POST or None)
    is_modal = request.GET.get('modal')
    status_code = 200
    if request.method == 'POST':
        if form.is_valid():
            person = form.save()
            if is_modal:
                response = json.dumps(serializers.PersonSerializer(person).data)
                return  HttpResponse(response, status=201, content_type='application/json')
            messages.success(request, "Person was created")
            return redirect(person.get_absolute_url())
        else:
            status_code = 400
            messages.warning(request, "Please correct errors below")
    context = {
        'form': form,
        'modal_title': "Add a new Person",
    }

    if is_modal:
        return render(request, 'modal_form.html', context, status=status_code)
    else:
        return render(request, 'events/person_form.html', context, status=status_code)

@login_required
@permission_required('events.change_event', raise_exception=PermissionDenied)
def contributors_events(request):
    events_date = request.GET.get('date', None)
    events_status = request.GET.get('status', None)
    events_missing = request.GET.get('missing', None)
    events_editable = request.GET.get('editable', None)

    count = request.GET.get('count', 20)
    page = request.GET.get('page', 1)

    # used to build a URL fragment that does not
    # contain "page" so that we can... paginate
    args = {'count': count}

    if events_editable:
        events = Event.objects.filter(editor_set__in=[request.user])
        args['editable'] = 'true'
    else:
        events = Event.objects.all()

    if events_date:
        if events_date == 'future':
            args['date'] = 'future'
            events = events.filter(start__gte=date.today())
        elif events_date == 'past':
            args['date'] = 'past'
            events = events.filter(start__lt=date.today())
    if events_status:
        args['status'] = events_status
        events = events.filter(status=events_status)
    if events_missing :
        if events_missing == 'title':
            args['missing'] = 'title'
            events = events.filter(title_not_announced=True)
        elif events_missing == 'location':
            args['missing'] = 'location'
            events = events.filter(location='')


    paginator = Paginator(events, count)

    try:
        events = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('contributors-events')

    fragment = '&'.join(["{k}={v}".format(k=k, v=v) for k, v in args.iteritems()])

    context = {
        'events': events,
        'fragment': fragment
    }

    return render(request, 'events/contributors_events.html', context)

@login_required()
@permission_required('events.change_eventgroup', raise_exception=PermissionDenied)
def contributors_eventgroups(request):
    eventgroups = EventGroup.objects.all()
    count = request.GET.get('count',20)
    page = request.GET.get('page', 1)

    paginator = Paginator(eventgroups, count)

    try:
        eventgroups = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('contributors-eventgroups')

    context = {
        'groups': eventgroups
    }

    return render(request, 'events/contributors_groups.html', context)

@login_required()
@permission_required('events.change_person', raise_exception=PermissionDenied)
def contributors_persons(request):
    persons = Person.objects.all()
    count = request.GET.get('count', 20)
    page = request.GET.get('page', 1)

    paginator = Paginator(persons, count)

    try:
        persons = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('contributors-persons')

    context = {
        'persons' : persons
    }

    return render(request, 'events/contributors_persons.html', context)

@login_required()
def show_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)

    context = {
        'person': person,
    }
    return render(request, 'events/person.html', context)


@login_required
@permission_required('events.change_person', raise_exception=PermissionDenied)
def edit_person(request, person_slug):
    person = get_object_or_404(Person, slug=person_slug)
    form = PersonForm(request.POST or None, instance=person)
    if request.method == 'POST':
        if form.is_valid():
            person = form.save()
            messages.success(request, "Person was updated")
            return redirect(person.get_absolute_url())
        else:
            messages.warning(request,"Please correct errors below")
    context = {
        'form': form,
        'person': person,
    }
    return render(request, 'events/person_form.html', context)
