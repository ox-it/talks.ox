from datetime import date, datetime, timedelta

from django.test import TestCase
from icalendar import Calendar
from rest_framework.exceptions import ParseError

from .renderers import ICalRenderer
from .utils import parse_date


class ICalSerializerTest(TestCase):

    def test_data(self):
        renderer = ICalRenderer()
        events = [{'url': 'http://oxtalks.com/test/1',
                   'title': 'Talk 1',
                   'description': 'Description'},
                  {'url': 'http://oxtalks.com/test/2',
                   'title': 'Talk 2',
                   'description': ''}]
        data = renderer.render(events)
        cal = Calendar.from_ical(data)
        self.assertEquals(len(cal.subcomponents), 2)
        self.assertEquals(cal.subcomponents[0]['SUMMARY'], 'Talk 1')
        self.assertEquals(cal.subcomponents[0]['DESCRIPTION'], 'Description')
        self.assertEquals(cal.subcomponents[0]['URL'], 'http://oxtalks.com/test/1')
        self.assertEquals(cal.subcomponents[1]['SUMMARY'], 'Talk 2')
        self.assertEquals(cal.subcomponents[1]['DESCRIPTION'], '')
        self.assertEquals(cal.subcomponents[1]['URL'], 'http://oxtalks.com/test/2')

    def test_event_to_ics(self):
        renderer = ICalRenderer()
        events = [{'url': 'http://oxtalks.com/test/1',
                   'title': 'Talk 1',
                   'description': 'Description'},
                  {'url': 'http://oxtalks.com/test/2',
                   'title': 'Talk 2',
                   'description': ''}]
        data = renderer.render(events)
        cal = Calendar.from_ical(data)
        self.assertEquals(len(cal.subcomponents), 2)
        self.assertEquals(cal.subcomponents[0]['SUMMARY'], 'Talk 1')
        self.assertEquals(cal.subcomponents[0]['DESCRIPTION'], 'Description')
        self.assertEquals(cal.subcomponents[0]['URL'], 'http://oxtalks.com/test/1')
        self.assertEquals(cal.subcomponents[1]['SUMMARY'], 'Talk 2')
        self.assertEquals(cal.subcomponents[1]['DESCRIPTION'], '')
        self.assertEquals(cal.subcomponents[1]['URL'], 'http://oxtalks.com/test/2')


class UtilsParseDate(TestCase):

    def test_today(self):
        result = parse_date("today")
        self.assertEquals(result, date.today())

    def test_tomorrow(self):
        result = parse_date("tomorrow")
        self.assertEquals(result, date.today() + timedelta(days=1))

    def test_invalid_date(self):
        self.assertRaises(ParseError, parse_date, "01/01/aa")

    def test_custom_date(self):
        result = parse_date("13/02/15")
        self.assertEquals(result, datetime(2015, 2, 13, 0, 0))
