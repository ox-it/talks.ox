import logging

import requests
from django.conf import settings

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render
from talks.old_talks.models import OldTalk, OldSeries
from talks.events.models import Event, EventGroup


logger = logging.getLogger(__name__)

def old_talks_mappings(request, index_id):
    eventList = OldTalk.objects.filter(old_talk_id=index_id).values_list('event', flat=True)
    if len(eventList):
        event = Event.objects.get(id=eventList[0]);
        return HttpResponsePermanentRedirect(reverse('show-event', args=[event.slug]))
    else:
        raise render(request, "old_talks/not_found.html")


def old_series_mappings(request, index_id):
    # Try series
    eventGroupList = OldSeries.objects.filter(old_series_id=index_id).values_list('group', flat=True)
    if len(eventGroupList):
        eventGroup = EventGroup.objects.get(id=eventGroupList[0]);
        return HttpResponsePermanentRedirect(reverse('show-event-group', args=[eventGroup.slug]))

    else:
        return render(request, "old_talks/not_found.html")