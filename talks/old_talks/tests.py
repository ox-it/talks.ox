from datetime import datetime
from django.test import TestCase

from talks.events.models import (Event, Person, PersonEvent,
                                 ROLES_SPEAKER, EventGroup, EVENT_PUBLISHED)
from .models import (event_to_old_talk, group_to_old_series,
                     get_list_id)


class TestOldTalks(TestCase):

    def test_event_to_old_talk(self):
        event = Event()
        event.title = u"TITLE"
        event.start = datetime(2014, 1, 1, 10, 30)
        event.end = datetime(2014, 1, 1, 11, 30)
        event.embargo = True
        event.save()

        s1 = Person()
        s1.name = "A"
        s1.save()

        s2 = Person()
        s2.name = "B"
        s2.save()

        event.save()

        PersonEvent.objects.create(person=s1, event=event, role=ROLES_SPEAKER)
        PersonEvent.objects.create(person=s2, event=event, role=ROLES_SPEAKER)

        data = event_to_old_talk(event, None)
        d = dict(data)

        self.assertEquals(len(data), 8)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[name_of_speaker]"], "A, B")
        self.assertEquals(d["talk[abstract]"], "")
        self.assertEquals(d["talk[date_string]"], "2014/01/01")
        self.assertEquals(d["talk[start_time_string]"], "10:30")
        self.assertEquals(d["talk[end_time_string]"], "11:30")
        self.assertEquals(d["talk[ex_directory]"], "1")

    def test_event_with_group_to_old_talk(self):
        event = Event()
        event.title = u"TITLE 2"
        event.description = "description"
        event.start = datetime(2014, 1, 1, 11, 00)
        event.end = datetime(2014, 1, 1, 12, 00)
        event.status = EVENT_PUBLISHED
        event.save()

        s = Person()
        s.name = "Personne"
        s.save()

        PersonEvent.objects.create(person=s, event=event, role=ROLES_SPEAKER)

        data = event_to_old_talk(event, "22")
        d = dict(data)

        self.assertEquals(len(data), 9)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[series_id_string]"], "22")
        self.assertEquals(d["talk[abstract]"], event.description+"\n")
        self.assertEquals(d["talk[name_of_speaker]"], s.name)
        self.assertEquals(d["talk[date_string]"], "2014/01/01")
        self.assertEquals(d["talk[start_time_string]"], "11:00")
        self.assertEquals(d["talk[end_time_string]"], "12:00")
        self.assertEquals(d["talk[ex_directory]"], "0")

    def test_group_to_old_series(self):
        group = EventGroup()
        group.title = "Group"
        group.save()

        data = group_to_old_series(group)
        d = dict(data)

        self.assertEquals(len(data), 1)
        self.assertEquals(d["list[name]"], group.title)

    def test_get_list_id(self):
        doc = """<?xml version="1.0" encoding="UTF-8"?>
                    <list>
                      <id>32</id>
                      <name>oOo</name>
                      <details></details>
                      <list_type></list_type>
                    </list>"""
        ident = get_list_id(doc)
        self.assertEquals(ident, "32")
