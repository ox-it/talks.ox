from __future__ import absolute_import
from datetime import datetime, timedelta
from icalendar.cal import Alarm

from rest_framework import renderers
from icalendar import Calendar, Event
from dateutil import parser

import pytz

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
        if 'ics_feed_title' in e:
            event.add('summary', e['ics_feed_title'])

        if 'description' in e:
            desc_status = ""
            if 'status' in e:
                if e['status'] == 'preparation':
                    desc_status = '\nStatus: This talk is in preparation - details may change\n'
                if e['status'] == 'cancelled':
                    desc_status = '\nStatus: This talk has been cancelled\n'

            desc_with_speakers = e['description']
            speakers_list = ""
            if 'various_speakers' in e and e['various_speakers'] is True:
                speakers_list = "\nSpeakers:\n Various Speakers"
            elif 'speakers' in e:
                if len(e['speakers']):
                    speakers_list = "\nSpeakers:\n" + ", ".join(speaker['get_name_with_bio'] for speaker in e['speakers'])
            event.add('description', desc_status + desc_with_speakers + speakers_list)

        if 'start' in e:
            event.add('dtstart', dt_string_to_object(e['start']))
        if 'end' in e:
            event.add('dtend', dt_string_to_object(e['end']))
        if 'full_url' in e:
            event.add('url', e['full_url'])
            event.add('uid', e['full_url'])
        if 'location' in e:
            event.add('location', e['location'])

        alarm = Alarm()
        alarm.add('action', 'display')
        alarm.add('trigger', timedelta(hours=-1))
        if 'ics_feed_title' in e:
            alarm.add('description', "Talk:" + e['ics_feed_title'])
        event.add_component(alarm)

        return event

def dt_string_to_object(string):
    """Transforms a string date into a datetime object
    :param string: string representing a date/time
    :return: python datetime object
    """
    oxfordtime = pytz.timezone('Europe/London')
    timeobj = parser.parse(string).astimezone(oxfordtime)
    return timeobj
