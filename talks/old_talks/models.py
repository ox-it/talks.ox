import logging

import requests

from django.dispatch.dispatcher import receiver
from django.db import models
from django.conf import settings

from talks.events.models import Event

logger = logging.getLogger(__name__)


@receiver(models.signals.post_save, sender=Event)
def update_old_talks(sender, instance, created, **kwargs):
    if hasattr(settings, "OLD_TALKS_SERVER") and hasattr(settings, "OLD_TALKS_USER") and hasattr(settings, "OLD_TALKS_PASSWORD"):
        data = event_to_old_talk(instance)

        url = "{server}/talk/update/".format(server=settings.OLD_TALKS_SERVER)

        logger.debug("POSTing {data} to {url}".format(data=data, url=url))

        response = requests.post(url, data, auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                 allow_redirects=True, stream=False, headers={"Accept": "application/xml"})

        if response.status_code != 200:
            raise Exception(response.status_code)


def event_to_old_talk(event):
    """Provide event data in old talks format
    :return:
    """
    data = [("talk[organiser_email]", "apiuser")]
    if event.title:
        data.append(("talk[title]", event.title))
    if event.description:
        data.append(("talk[abstract]", event.description))
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
