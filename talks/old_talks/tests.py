from django.test import TestCase

from talks.events.models import Event
from .models import event_to_old_talk


class TestOldTalks(TestCase):

    def test_talk(self):
        event = Event()
        event.title = u"TITLE"
        event.save()

        data = event_to_old_talk(event)
        d = dict(data)
        self.assertEquals(len(data), 2)
        self.assertEquals(d["talk[title]"], event.title)
