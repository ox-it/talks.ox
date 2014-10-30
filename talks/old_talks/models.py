import logging
from xml.etree import ElementTree

from django.db import models
from django.dispatch.dispatcher import receiver

from talks.events.models import Event, EventGroup

logger = logging.getLogger(__name__)


class OldTalk(models.Model):
    event = models.ForeignKey(Event, null=False)
    old_talk_id = models.CharField(max_length=20, null=False, blank=False)


class OldSeries(models.Model):
    group = models.ForeignKey(EventGroup, null=False)
    old_series_id = models.CharField(max_length=20, null=False, blank=False)


@receiver(models.signals.post_save, sender=Event)
def publish_to_old_talks(sender, instance, created, **kwargs):
    from .tasks import update_old_talks
    update_old_talks(instance)


def get_list_id(string):
    """Get the list ID from the response (as a string)
    :param string: response content
    :return: list identifier
    """
    doc = ElementTree.fromstring(string)
    return doc.find("id").text


def event_to_old_talk(event):
    """Provide event data in old talks format
    :param event: django model Event
    :return: list of tuples
    """
    data = [("talk[organiser_email]", "apiuser")]   # TODO pending extension of data model will need to be updated
    if event.title:
        data.append(("talk[title]", event.title))
    else:
        data.append(("talk[title]", "To be announced"))
    if event.description:
        data.append(("talk[abstract]", event.description))
    else:
        data.append(("talk[abstract]", ""))
    if event.start:
        data.append(("talk[date_string]", event.start.strftime("%Y/%m/%d")))
        data.append(("talk[start_time_string]", event.start.strftime("%H:%M")))
    if event.end:
        data.append(("talk[end_time_string]", event.end.strftime("%H:%M")))
    if event.location:
        data.append(("talk[venue_name]", event.location.identifier))
    if len(event.speakers.all()) > 0:
        data.append(("talk[name_of_speaker]", ", ".join([speaker.name for speaker in event.speakers.all()])))
    return data


def group_to_old_series(group):
    """Provide list data in old talks format
    :param group: django model EventGroup
    :return: list of tuples
    """
    data = []
    data.append(('list[name]', group.title))
    return data
