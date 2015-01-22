import logging
import json
from datetime import date
from functools import partial

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from talks.events.models import Event, EventGroup, Person, ROLES_SPEAKER
from talks.contributors.forms import EventForm, EventGroupForm, PersonQuickAdd, PersonForm
from talks.api import serializers
from talks.events.signals import event_updated, eventgroup_updated

logger = logging.getLogger(__name__)

@login_required
@permission_required('events.change_event', raise_exception=PermissionDenied)
def edit_event(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    if not event.user_can_edit(request.user):
        raise PermissionDenied
    # providing data for topics/speakers as it is not straight from the Model
    initial = {'topics': [t.uri for t in event.topics.all()],   # uses GenericRelation
               'speakers': event.speakers.all(),        # different of person_set
               'organisers': event.organisers.all(),
               'hosts': event.hosts.all()}
    form = EventForm(request.POST or None, instance=event, initial=initial, prefix='event', user=request.user)
    context = {
        'event': event,
        'event_form': form,
        'speaker_form': PersonQuickAdd(),
        'organiser_form': PersonQuickAdd(),
        'host_form': PersonQuickAdd(),
        'is_editing': True,
    }
    if request.method == 'POST':
        if form.is_valid():
            event = form.save()
            if request.user not in event.editor_set.all():
                event.editor_set.add(request.user)
                event.save()
            event_updated.send(event.__class__, instance=event)
            messages.success(request, "Talk was updated")
            return redirect(event.get_absolute_url())
        else:
            messages.warning(request, "Please correct errors below")
    return render(request, "contributors/event_form.html", context)

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

    print request.user

    PrefixedEventForm = partial(EventForm, prefix='event', initial=initial, user=request.user)

    if request.method == 'POST':
        context = {
            'event_form': PrefixedEventForm(request.POST),
            'speaker_form': PersonQuickAdd(),
            'organiser_form': PersonQuickAdd(),
            'host_form': PersonQuickAdd(),
        }
        forms_valid = context['event_form'].is_valid()
        if forms_valid:
            logging.debug("form is valid")
            event = context['event_form'].save()
            if request.user not in event.editor_set.all():
                event.editor_set.add(request.user)
                event.save()
            event_updated.send(event.__class__, instance=event)
            messages.success(request, "New talk has been created")
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
            'speaker_form': PersonQuickAdd(),
            'organiser_form': PersonQuickAdd(),
            'host_form': PersonQuickAdd,
            'is_editing': False
        }
    return render(request, 'contributors/event_form.html', context)


@login_required
@permission_required('events.delete_event', raise_exception=PermissionDenied)
def delete_event(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)

    # only super users or editors can delete an event
    if not event.user_can_edit(request.user):
        raise PermissionDenied

    # if the user is not a super user, and if the event has already started
    # it should not be possible to delete it
    if not request.user.is_superuser:
        if event.already_started:
            messages.warning(request, "You cannot delete a talk that has already started")
            return redirect(event.get_absolute_url())
    context = {
        'event': event,
    }
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Talk has been successfully deleted")
        return redirect('contributors-events')
    return render(request, "contributors/delete_event.html", context)

@login_required
@permission_required('events.change_eventgroup', raise_exception=PermissionDenied)
def edit_event_group(request, event_group_slug):
    group = get_object_or_404(EventGroup, slug=event_group_slug)
    if not group.user_can_edit(request.user):
        raise PermissionDenied

    form = EventGroupForm(request.POST or None, instance=group)
    if request.method == 'POST':
        logging.debug("incoming post: %s", request.POST)
        if form.is_valid():
            event_group = form.save()
            if request.user not in event_group.editor_set.all():
                event_group.editor_set.add(request.user)
                event_group.save()
            eventgroup_updated.send(event_group.__class__, instance=event_group)
            messages.success(request, "Series was updated")
            return redirect(event_group.get_absolute_url())
        else:
            messages.warning(request, "Please correct errors below")
    context = {
        'group_form': form,
        'organiser_form': PersonQuickAdd(),
        'event_group': group,
        'is_editing': True
    }
    return render(request, 'contributors/event_group_form.html', context)


@login_required
@permission_required('events.add_eventgroup', raise_exception=PermissionDenied)
def create_event_group(request):
    form = EventGroupForm(request.POST or None)
    is_modal = request.GET.get('modal')
    status_code = 200
    if request.method == 'POST':
        if form.is_valid():
            event_group = form.save()
            eventgroup_updated.send(event_group.__class__, instance=event_group)
            if is_modal:
                response = json.dumps(serializers.EventGroupSerializer(event_group).data)
                return HttpResponse(response, status=201, content_type='application/json')
            messages.success(request, "Series was created")
            return redirect(event_group.get_absolute_url())
        else:
            status_code = 400
            messages.warning(request, "Please correct errors below")

    context = {
        'group_form': form,
        'organiser_form': PersonQuickAdd(),
        'modal_title': "Add a new series",
        'is_editing': False
    }

    if is_modal:
        return render(request, 'contributors/event_group_modal_form.html', context, status=status_code)
    else:
        return render(request, 'contributors/event_group_form.html', context, status=status_code)


@login_required
@permission_required('events.delete_eventgroup', raise_exception=PermissionDenied)
def delete_event_group(request, event_group_slug):
    event_group = get_object_or_404(EventGroup, slug=event_group_slug)
    if not event_group.user_can_edit(request.user):
        raise PermissionDenied
    context = {
        'event_group': event_group,
        'events': event_group.events.all()
    }
    if request.method == 'POST':
        # first updating all events that were referring to the group to be deleted
        Event.objects.filter(group=event_group).update(group=None)
        event_group.delete()
        messages.success(request, "Series has been successfully deleted")
        return redirect('contributors-events')
    return render(request, "contributors/delete_event_group.html", context)


def contributors_home(request):
    return HttpResponseRedirect(reverse('contributors-events'))


@login_required()
@permission_required('events.add_person', raise_exception=PermissionDenied)
def create_person(request):
    form = PersonForm(request.POST or None)
    status_code = 200
    if request.method == 'POST':
        if form.is_valid():
            person = form.save()
            messages.success(request, "Person was created")
            return redirect(person.get_absolute_url())
        else:
            status_code = 400
            messages.warning(request, "Please correct errors below")
    context = {
        'person_form': form,
    }

    return render(request, 'contributors/person_form.html', context, status=status_code)

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

    if events_editable and not request.user.is_superuser:
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
        elif events_missing == 'speaker':
            args['missing'] = 'speaker'
            events = events.exclude(personevent__role=ROLES_SPEAKER)

    events = events.order_by('start')
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

    return render(request, 'contributors/contributors_events.html', context)


@login_required()
@permission_required('events.change_eventgroup', raise_exception=PermissionDenied)
def contributors_eventgroups(request):
    groups_editable = request.GET.get('editable', None)
    count = request.GET.get('count',20)
    page = request.GET.get('page', 1)

    args={'count': count}

    if groups_editable and not request.user.is_superuser:
        eventgroups = EventGroup.objects.filter(editor_set__in=[request.user])
        args['editable'] = 'true'
    else:
        eventgroups = EventGroup.objects.all()

    eventgroups = eventgroups.order_by('title')

    paginator = Paginator(eventgroups, count)

    try:
        eventgroups = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('contributors-eventgroups')

    fragment = '&'.join(["{k}={v}".format(k=k, v=v) for k,v in args.iteritems()])

    context = {
        'groups': eventgroups,
        'fragment': fragment
    }

    return render(request, 'contributors/contributors_groups.html', context)


@login_required()
@permission_required('events.change_person', raise_exception=PermissionDenied)
def contributors_persons(request):
    persons = Person.objects.all()
    count = request.GET.get('count', 20)
    page = request.GET.get('page', 1)

    persons = sorted(persons, key=lambda person: person.surname)

    paginator = Paginator(persons, count)

    try:
        persons = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        return redirect('contributors-persons')

    context = {
        'persons': persons
    }

    return render(request, 'contributors/contributors_persons.html', context)


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
        'person_form': form,
        'person': person,
    }
    return render(request, 'contributors/person_form.html', context)
