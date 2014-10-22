import logging

from datetime import date
from functools import partial
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import Event, EventGroup, Speaker
from .forms import EventForm, EventGroupForm, SpeakerQuickAdd
from talks.events.models import TopicItem, Topic

logger = logging.getLogger(__name__)


def homepage(request):
    events = Event.objects.todays_events()
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


def event(request, event_id):
    try:
        ev = Event.objects.select_related(
            'speakers',
            'location',
            'group',
            'department_organiser').get(id=event_id)
    except Event.DoesNotExist:
        raise Http404
    context = {
        'event': ev,
        'speakers': ev.speakers.all(),
    }
    return render(request, 'events/event.html', context)


def create_event(request, group_id=None):
    initial = None
    group = None
    logger.debug("group_id:%s", group_id)
    if group_id:
        group = get_object_or_404(EventGroup, pk=group_id)
        initial = {
            'event_group_select': group,
            'enabled': True,
        }

    PrefixedEventForm = partial(EventForm, prefix='event')
    PrefixedEventGroupForm = partial(EventGroupForm, prefix='event-group',
                                     initial=initial)

    if request.method == 'POST':
        context = {
            'event_form': PrefixedEventForm(request.POST),
            'event_group_form': PrefixedEventGroupForm(request.POST),
            'speaker_form': SpeakerQuickAdd(),
        }
        forms_valid = context['event_form'].is_valid() and context['event_group_form'].is_valid()
        if forms_valid:
            event_group = context['event_group_form'].get_event_group() or group
            event = context['event_form'].save(commit=False)
            if event_group:
                event_group.save()
                event.group = event_group
            event.save()

            # saving topics
            event_topics = context['event_form'].cleaned_data['topics']
            event_ct = ContentType.objects.get_for_model(Event)
            for topic in event_topics:
                TopicItem.objects.create(topic=topic,
                                         content_type=event_ct,
                                         object_id=event.id)

            # *Now* we can save the many2many relations
            context['event_form'].save_m2m()
            if 'another' in request.POST:
                if event_group:
                    logger.debug("redirecting to create-event-in-group")
                    # Adding more events, redirect to the create event in existing group form
                    return HttpResponseRedirect(reverse('create-event-in-group', args=(event_group.id,)))
                else:
                    logger.debug("redirecting to create-event")
                    return HttpResponseRedirect(reverse('create-event'))
            else:
                return HttpResponseRedirect(reverse('event', args=(event.id,)))
        else:
            if 'speakers' in context['event_form'].cleaned_data:
                context['selected_speakers'] = Speaker.objects.filter(
                    id__in=context['event_form'].cleaned_data['speakers'])
            if 'topics' in context['event_form'].cleaned_data:
                context['selected_topics'] = Topic.objects.filter(
                    id__in=context['event_form'].cleaned_data['topics'])
    else:
        context = {
            'event_form': PrefixedEventForm(),
            'event_group_form': PrefixedEventGroupForm(),
            'speaker_form': SpeakerQuickAdd(),
        }
    return render(request, 'events/create_event.html', context)


def event_group(request, event_group_id):
    try:
        # Cache the 'events' objects on the EventGroup
        evg = EventGroup.objects.prefetch_related('events'
                                                  ).get(id=event_group_id)
    except EventGroup.DoesNotExist:
        raise Http404
    context = {
        'event_group': evg,
    }
    return render(request, 'events/event-group.html', context)
