from datetime import datetime
from django.test import TestCase

from talks.events.models import (Event, Person, PersonEvent,
                                 ROLES_SPEAKER, EventGroup, EVENT_PUBLISHED, AUDIENCE_OXFORD, ROLES_HOST)
from .models import (event_to_old_talk, group_to_old_series,
                     get_list_id)


class TestOldTalks(TestCase):

    def test_event_to_old_talk(self):
        event = Event()
        event.title = u"TITLE"
        event.start = datetime(2014, 1, 1, 10, 30)
        event.end = datetime(2014, 1, 1, 11, 30)
        event.embargo = True
        event.booking_email = "test@test.com"
        event.audience = AUDIENCE_OXFORD
        event.location_details = "upstairs"
        event.save()

        s1 = Person()
        s1.name = "A"
        s1.bio = "Abio"
        s1.save()

        s2 = Person()
        s2.name = "B"
        s2.bio = "Bbio"
        s2.save()

        s3 = Person()
        s3.name = "C"
        s3.bio = "Cbio"
        s3.save()

        event.save()

        PersonEvent.objects.create(person=s1, event=event, role=ROLES_SPEAKER)
        PersonEvent.objects.create(person=s2, event=event, role=ROLES_SPEAKER)
        PersonEvent.objects.create(person=s3, event=event, role=ROLES_HOST)

        data = event_to_old_talk(event, None)
        d = dict(data)

        self.assertEquals(len(data), 8)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[name_of_speaker]"], "A (Abio), B (Bbio)")
        self.assertTrue("Email address for booking: test@test.com" in d["talk[abstract]"])
        self.assertTrue("Members of the University only" in d["talk[abstract]"])
        self.assertTrue("Booking: Not required" in d["talk[abstract]"])
        self.assertTrue("Hosts: C (Cbio)" in d["talk[abstract]"])
        self.assertFalse("Organisers:" in d["talk[abstract]"])
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
        s.bio = "b"
        s.save()
        PersonEvent.objects.create(person=s, event=event, role=ROLES_SPEAKER)

        p = Person()
        p.name = "H"
        p.bio = "bio"
        p.save()
        PersonEvent.objects.create(person=p, event=event, role=ROLES_HOST)

        data = event_to_old_talk(event, "22")
        d = dict(data)

        self.assertEquals(len(data), 9)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[series_id_string]"], "22")
        self.assertTrue(event.description+"\n" in d["talk[abstract]"])
        self.assertTrue("Hosts: H (bio)" in d["talk[abstract]"])
        self.assertFalse("Organisers: " in d["talk[abstract]"])
        self.assertEquals(d["talk[name_of_speaker]"], s.name + " (" + s.bio + ")")
        self.assertEquals(d["talk[date_string]"], "2014/01/01")
        self.assertEquals(d["talk[start_time_string]"], "11:00")
        self.assertEquals(d["talk[end_time_string]"], "12:00")
        self.assertEquals(d["talk[ex_directory]"], "0")
        self.assertTrue(event.location_details in d["talk[venue_name]"])

    def test_group_to_old_series(self):
        group = EventGroup()
        group.title = "Group"
        group.description = "group description"
        group.save()

        o = Person()
        o.name = "Organising person"
        o.save()
        group.organisers.add(o)

        group.save()

        data = group_to_old_series(group)
        d = dict(data)

        self.assertEquals(len(data), 2)
        self.assertEquals(d["list[name]"], group.title)
        self.assertTrue(group.description+"\n" in d["list[details]"])
        self.assertTrue("Organisers: Organising person" in d["list[details]"])

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
