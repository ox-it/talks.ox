import logging

from datetime import date
from functools import partial
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

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
    event_group = None
    logger.debug("group_id:%s", group_id)
    if group_id:
        event_group = get_object_or_404(EventGroup, pk=group_id)
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
            event = context['event_form'].save(commit=False)
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
            'speaker_form': SpeakerQuickAdd(),
        }
    return render(request, 'events/create_event.html', context)


def list_event_groups(request):
    object_list = EventGroup.objects.all()
    context = {
        'object_list': object_list,
    }
    return render(request, "events/event_group_list.html", context)


def show_event_group(request, event_group_id):
    group = get_object_or_404(EventGroup, pk=event_group_id)
    context = {
        'event_group': group,
    }
    return render(request, 'events/event-group.html', context)


def edit_event_group(request, event_group_id):
    group = get_object_or_404(EventGroup, pk=event_group_id)
    form = EventGroupForm(request.POST or None, instance=group)
    if request.method == 'POST':
        logging.debug("incoming post: %s", request.POST)
        if form.is_valid():
            event_group = form.save()
            return redirect(event_group.get_absolute_url())

    context = {
        'form': form,
        'event_group': group,
    }
    return render(request, 'events/event_group_form.html', context)


def create_event_group(request):
    form = EventGroupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            event_group = form.save()
            return redirect(event_group.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'events/event_group_form.html', context)
