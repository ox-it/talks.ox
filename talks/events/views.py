from django.shortcuts import render


def homepage(request):
    return render(request, 'events/events.html', {})


def upcoming_events(request):
    pass


def events_for_year(request, year):
    pass


def events_for_month(request, year, month):
    pass


def events_for_day(request, year, month, day):
    pass


def event(request, event_id):
    pass
