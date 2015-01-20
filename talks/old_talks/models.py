import logging
from xml.etree import ElementTree

from django.db import models
from django.dispatch.dispatcher import receiver

from talks.events.models import Event, EventGroup, AUDIENCE_CHOICES, AUDIENCE_OXFORD, BOOKING_CHOICES
from talks.events.signals import event_updated, eventgroup_updated

logger = logging.getLogger(__name__)


class OldTalk(models.Model):
    event = models.ForeignKey(Event, null=False)
    old_talk_id = models.CharField(max_length=20, null=False, blank=False)


class OldSeries(models.Model):
    group = models.ForeignKey(EventGroup, null=False)
    old_series_id = models.CharField(max_length=20, null=False, blank=False)


@receiver(event_updated, sender=Event)
def publish_to_old_talks(sender, instance, *args, **kwargs):
    from talks.old_talks.tasks import update_old_talks
    update_old_talks(instance)


@receiver(eventgroup_updated, sender=EventGroup)
def update_series_old_talks(sender, instance, *args, **kwargs):
    from talks.old_talks.tasks import update_old_series
    update_old_series(instance, True)


@receiver(models.signals.post_delete, sender=Event)
def delete_old_talks(sender, instance, using, **kwargs):
    from .tasks import delete_old_talks
    delete_old_talks(instance)


def get_list_id(string):
    """Get the list ID from the response (as a string)
    :param string: response content
    :return: list identifier
    """
    doc = ElementTree.fromstring(string)
    return doc.find("id").text


def event_to_old_talk(event, series_id):
    """Provide event data in old talks format
    :param event: django model Event
    :return: list of tuples
    """
    data = [("talk[organiser_email]", event.organiser_email)]
    if event.title:
        data.append(("talk[title]", event.title))
    else:
        data.append(("talk[title]", "To be announced"))
    data.append(("talk[abstract]", build_abstract(event)))
    if event.start:
        data.append(("talk[date_string]", event.start.strftime("%Y/%m/%d")))
        data.append(("talk[start_time_string]", event.start.strftime("%H:%M")))
    if event.end:
        data.append(("talk[end_time_string]", event.end.strftime("%H:%M")))
    if event.location:
        location = event.api_location
        data.append(("talk[venue_name]", "{name}, {address}".format(name=location['name'], address=location.get('address', ''))))
    if series_id:
        data.append(("talk[series_id_string]", series_id))
    if len(event.speakers.all()) > 0:
        data.append(("talk[name_of_speaker]", ", ".join([speaker.name for speaker in event.speakers.all()])))
    # sets the ex_directory status all the time to be sure to be in sync
    if event.is_published:
        data.append(("talk[ex_directory]", "0"))
    else:
        data.append(("talk[ex_directory]", "1"))
    return data


def build_abstract(event):
    abstract = ""
    if event.description:
        abstract += event.description
        abstract += "\n"
    if event.topics.count() > 0:
        topics = event.api_topics
        abstract += "\nTopics: " + ", ".join([topic['prefLabel'] for topic in topics])
    if event.hosts.count() > 0:
        abstract += "\nHosts: " + ", ".join([host.name for host in event.hosts.all()])
    if event.organisers.count() > 0:
        abstract += "\nOrganisers: " + ", ".join([organiser.name for organiser in event.organisers.all()])
    if event.organiser_email:
        abstract += "\nContact email: " + event.organiser_email
    abstract += "\nAudience: " + dict(AUDIENCE_CHOICES)[event.audience]
    abstract += "\nBooking: " + dict(BOOKING_CHOICES)[event.booking_type]
    if event.booking_url:
        abstract += "\nWeb address for booking: " + event.booking_url
    if event.booking_email:
        abstract += "\nEmail address for booking: " + event.booking_email
    if event.cost:
        abstract += "\nCost: " + event.cost

    return abstract


def group_to_old_series(group):
    """Provide list data in old talks format
    :param group: django model EventGroup
    :return: list of tuples
    """
    data = []
    data.append(('list[name]', group.title))

    description = group.description
    if group.organisers.count() > 0:
        description += "\nOrganisers: " + ", ".join([organiser.name for organiser in group.organisers.all()])

    data.append(('list[description]', description))
    return data
