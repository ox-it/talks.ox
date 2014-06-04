from datetime import date

from django.http.response import Http404
from django.shortcuts import render

from talks.api_ox.query import get_info, get_oxford_date
from talks.api_ox.api import ApiException
from .models import Event


def homepage(request):
    # TODO needs to clarify the difference
    # between homepage and upcoming_events?
    return upcoming_events(request)


def upcoming_events(request):
    today = date.today()
    events = Event.objects.filter(start__gte=today)
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
        oxford_date = get_oxford_date(ev.start)
        context['oxford_date'] = oxford_date['formatted']
    else:
        raise Http404
    return render(request, 'events/event.html', context)
