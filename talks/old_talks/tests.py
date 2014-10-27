from django.test import TestCase

from talks.events.models import Event, Speaker
from .models import event_to_old_talk


class TestOldTalks(TestCase):

    def test_talk(self):
        event = Event()
        event.title = u"TITLE"
        event.save()

        s1 = Speaker()
        s1.name = "A"
        s1.save()

        s2 = Speaker()
        s2.name = "B"
        s2.save()

        event.speakers.add(s1, s2)
        event.save()

        data = event_to_old_talk(event)
        d = dict(data)

        self.assertEquals(len(data), 3)
        self.assertEquals(d["talk[title]"], event.title)
        self.assertEquals(d["talk[name_of_speaker]"], "A, B")
