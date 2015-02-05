import logging
from haystack.query import SearchQuerySet

import requests

from django.http.response import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)


def healthcheck(request):
    checks = {'DB': _test_db_connection,
              'Topics': _test_topics_connection,
              'Events search': _test_events_search}
    response = HttpResponse()
    overall_ok = True
    for name, service in checks.iteritems():
        try:
            ok, message = service()
        except Exception as e:
            ok = False
            message = e
            logger.error('Error in healthcheck {name}'.format(name=name), exc_info=True)
        if not ok:
            overall_ok = False
            response.write('* !! {service}: {text}\n'.format(service=name, text=message))
        else:
            response.write('* {service}: {text}\n'.format(service=name, text=message.replace('\n', '')))
    response['Content-Type'] = "text/plain; charset=utf-8"
    response['Cache-Control'] = "must-revalidate,no-cache,no-store"
    if overall_ok:
        response.status_code = 200
    else:
        response.status_code = 500
    return response


def _test_db_connection():
    from talks.events.models import Event
    try:
        count = Event.objects.count()
        if count == 0:
            return False, "Event.objects.count() == 0!"
        else:
            return True, "OK"
    except Exception as e:
        return False, e.message


def _test_topics_connection():
    """Performs a healthcheck to the configured client
    """
    if not settings.TOPICS_URL:
        return False, "TOPICS_URL is not configured"
    try:
        response = requests.get('{server}search?q=a'.format(server=settings.TOPICS_URL),
                                timeout=2)
        response.raise_for_status()
        return response.ok, "OK"
    except Exception as e:
        return False, e


def _test_events_search():
    try:
        SearchQuerySet().filter(content='*:*').count()
        return True, "OK"
    except Exception as e:
        return False, e.message
