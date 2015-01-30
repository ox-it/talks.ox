from rest_framework import renderers
from icalendar import Calendar, Event


class ICalRenderer(renderers.BaseRenderer):
    media_type = 'text/calendar'
    format = 'ics'

    def render(self, data, media_type=None, renderer_context=None):
        cal = Calendar()
        cal.add('prodid', 'talks.ox.ac.uk')
        cal.add('version', '2.0')

        for e in data:
            cal.add_component(self._event_to_ics(e))
        return cal.to_ical()

    @staticmethod
    def _event_to_ics(e):
        event = Event()
        if 'title' in e:
            event.add('summary', e['title'])
        if 'description' in e:
            event.add('description', e['description'])
        if 'start' in e:
            event.add('dtstart', e['start'])
        if 'url' in e:
            event.add('url', e['url'])
            event.add('uid', e['url'])
        # TODO add location field
        return event
