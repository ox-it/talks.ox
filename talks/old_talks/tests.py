from django.test import TestCase

from talks.events.models import (Event, Person, PersonEvent,
                                 ROLES_SPEAKER, EventGroup)
from .models import (event_to_old_talk, group_to_old_series,
                     get_list_id)


class TestOldTalks(TestCase):

    def test_event_to_old_talk(self):
        event = Event()
        event.title = u"TITLE"
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

        self.assertEquals(len(data), 4)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[name_of_speaker]"], "A, B")
        self.assertEquals(d["talk[abstract]"], "")

    def test_event_with_group_to_old_talk(self):
        event = Event()
        event.title = u"TITLE 2"
        event.description = "description"
        event.save()

        s = Person()
        s.name = "Personne"
        s.save()

        PersonEvent.objects.create(person=s, event=event, role=ROLES_SPEAKER)

        data = event_to_old_talk(event, "22")
        d = dict(data)

        self.assertEquals(len(data), 5)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[series_id_string]"], "22")
        self.assertEquals(d["talk[abstract]"], event.description)
        self.assertEquals(d["talk[name_of_speaker]"], s.name)

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
