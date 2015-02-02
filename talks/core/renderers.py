from datetime import datetime

from rest_framework import renderers
from icalendar import Calendar, Event


class ICalRenderer(renderers.BaseRenderer):
    media_type = 'text/calendar'
    format = 'ics'

    def render(self, data, media_type=None, renderer_context=None):
        cal = Calendar()
        cal.add('prodid', 'talks.ox.ac.uk')
        cal.add('version', '2.0')

        if not isinstance(data, list):
            data = [data]

        for e in data:
            cal.add_component(self._event_to_ics(e))
        return cal.to_ical()

    @staticmethod
    def _event_to_ics(e):
        event = Event()
        if 'title' in e and e['title'] != '':
            event.add('summary', e['title'])
        else:
            event.add('summary', 'Untitled talks.ox')
        if 'description' in e:
            event.add('description', e['description'])
        if 'start' in e:
            event.add('dtstart', dt_string_to_object(e['start']))
        if 'end' in e:
            event.add('dtend', dt_string_to_object(e['end']))
        if 'url' in e:
            event.add('url', e['url'])
            event.add('uid', e['url'])
        # TODO add location field
        return event


def dt_string_to_object(string):
    """Transforms a string date into a datetime object
    :param string: string representing a date/time
    :return: python datetime object
    """
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
