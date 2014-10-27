from django.test import TestCase

from talks.events.models import Event
from .models import event_to_old_talk


class TestOldTalks(TestCase):

    def test_talk(self):
        event = Event()
        event.title = "TITLE"

        data = event_to_old_talk(event)
        self.assertEquals(len(data), 2)
