import logging

import requests
from django.conf import settings

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from talks.old_talks.models import OldTalk, OldSeries
from talks.events.models import Event


logger = logging.getLogger(__name__)

def old_talks_mappings(request, index_id):
    eventList = OldTalk.objects.filter(old_talk_id=index_id).values_list('event', flat=True)
    if len(eventList):
        event = Event.objects.get(id=eventList[0]);
        return HttpResponsePermanentRedirect(reverse('show-event', args=[event.slug]))

    else:
        raise Http404;