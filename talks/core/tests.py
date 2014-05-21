from django.test import TestCase
from icalendar import Calendar

from .renderers import ICalRenderer


class ICalSerializerTest(TestCase):

    def test_data(self):
        renderer = ICalRenderer()
        events = [{'url': 'http://oxtalks.com/test/1',
                   'title': 'Talk 1',
                   'description': 'Description'},
                  {'url': 'http://oxtalks.com/test/2',
                   'title': 'Talk 2',
                   'description': ''}]
        data = renderer.render({'results': events})
        cal = Calendar.from_ical(data)
        self.assertEquals(len(cal.subcomponents), 2)
        self.assertEquals(cal.subcomponents[0]['SUMMARY'], 'Talk 1')
        self.assertEquals(cal.subcomponents[0]['DESCRIPTION'], 'Description')
        self.assertEquals(cal.subcomponents[0]['URL'], 'http://oxtalks.com/test/1')
        self.assertEquals(cal.subcomponents[1]['SUMMARY'], 'Talk 2')
        self.assertEquals(cal.subcomponents[1]['DESCRIPTION'], '')
        self.assertEquals(cal.subcomponents[1]['URL'], 'http://oxtalks.com/test/2')
