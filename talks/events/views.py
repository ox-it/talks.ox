import logging

from datetime import date
from functools import partial

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms

from talks.api_ox.query import get_info, get_oxford_date
from talks.api_ox.api import ApiException
from .models import Event
from .forms import EventForm, EventGroupForm

logger = logging.getLogger(__name__)


def homepage(request):
    # TODO needs to clarify the difference
    # between homepage and upcoming_events?
    return upcoming_events(request)


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
    ev = Event.objects.get(id=event_id)
    if ev:
        context = {'event': ev}
        if ev.location:
            context['location_name'] = ev.location.name
            try:
                location = get_info(ev.location.identifier)
            except ApiException:
                location = None
            if location:
                context['location'] = location
        formatted = None
        if ev.start:
            try:
                oxford_date = get_oxford_date(ev.start)
                formatted = oxford_date['formatted'] if 'formatted' in oxford_date else None
            except ApiException:
                logger.warn('Unable to reach API', exc_info=True)
        context['oxford_date'] = formatted
    else:
        raise Http404
    return render(request, 'events/event.html', context)


def create_event(request):
    PrefixedEventForm = partial(EventForm, prefix='event')
    PrefixedEventGroupForm = partial(EventGroupForm, prefix='event-group')

    if request.method=='POST':
        context = {
            'event_form': PrefixedEventForm(request.POST),
            'event_group_form': PrefixedEventGroupForm(request.POST),
        }
        forms_valid = context['event_form'].is_valid and context['event_group_form'].is_valid()
        if forms_valid:
            event_group = context['event_group_form'].get_event_group()
            event = context['event_form'].save(commit=False)
            if event_group:
                event_group.save()
                event.group = event_group
            event.save()
            return HttpResponseRedirect(reverse('event', args=(event.id,)))
    else:
        context = {
            'event_form': PrefixedEventForm(),
            'event_group_form': PrefixedEventGroupForm(),
        }
    return render(request, 'events/create_event.html', context)
