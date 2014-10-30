import logging

import requests

from django.dispatch.dispatcher import receiver
from django.db import models
from django.conf import settings

from talks.events.models import Event, EventGroup

logger = logging.getLogger(__name__)


class OldTalk(models.Model):
    event = models.ForeignKey(Event, null=False)
    old_talk_id = models.CharField(max_length=20, null=False, blank=False)


class OldSeries(models.Model):
    group = models.ForeignKey(EventGroup, null=False)
    old_series_id = models.CharField(max_length=20, null=False, blank=False)


@receiver(models.signals.post_save, sender=Event)
def update_old_talks(sender, instance, created, **kwargs):
    if hasattr(settings, "OLD_TALKS_SERVER") and hasattr(settings, "OLD_TALKS_USER") and hasattr(settings, "OLD_TALKS_PASSWORD"):
        data = event_to_old_talk(instance)

        old_talk, is_new = OldTalk.objects.get_or_create(event=instance)

        if is_new:
            url = "{server}/talk/update/".format(server=settings.OLD_TALKS_SERVER)
        else:
            url = "{server}/talk/update/{id}".format(server=settings.OLD_TALKS_SERVER,
                                                     id=old_talk.old_talk_id)

        logger.debug("POSTing {data} to {url}".format(data=data, url=url))

        response = requests.post(url, data, auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                 allow_redirects=True, stream=False, headers={"Accept": "application/xml"})

        if response.status_code == 200:
            if is_new:
                if 'location' in response.headers:
                    talk_url = response.headers['location']
                    talk_id = talk_url.split("/")[-1]
                    old_talk.old_talk_id = talk_id
                    old_talk.save()
                else:
                    raise Exception("Didn't got the location header so cannot say which talk this is")
        else:
            raise Exception(response.status_code)


def event_to_old_talk(event):
    """Provide event data in old talks format
    :return:
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
