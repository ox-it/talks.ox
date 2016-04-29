from datetime import datetime, timedelta
from icalendar.cal import Alarm

from rest_framework import renderers
from icalendar import Calendar, Event
from dateutil import parser


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
        event.add('summary', e['title_display'])
        if 'description' in e:
            desc_status = "" 
            if e['status'] == 'preparation':
                desc_status = '\nStatus: This talk is in preparation - details may change\n'
                
            desc_with_speakers = e['description']
            speakers_list = ""
            if 'speakers' in e:
                if len(e['speakers']):
                    speakers_list = "\nSpeakers:\n" + ", ".join(get_speaker_name(speaker) for speaker in e['speakers'])
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
        alarm.add('description', "Talk:" + e['title_display'])
        event.add_component(alarm)

        return event


def get_speaker_name(speaker):
    name = speaker['name']
    if(speaker['bio']):
        name += " (" + speaker['bio'] + ")"
    return name

def dt_string_to_object(string):
    """Transforms a string date into a datetime object
    :param string: string representing a date/time
    :return: python datetime object
    """
    return parser.parse(string)
