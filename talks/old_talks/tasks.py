import logging

import requests
from django.conf import settings

from talks.old_talks.models import (OldTalk, OldSeries, event_to_old_talk,
                                    get_list_id, group_to_old_series)

logger = logging.getLogger(__name__)


def update_old_talks(event):
    if _old_talks_configured():
        if event.group:
            old_series = update_old_series(event.group, False)
            data = event_to_old_talk(event, old_series.old_series_id)
        else:
            data = event_to_old_talk(event, None)

        old_talk, is_new = OldTalk.objects.get_or_create(event=event)

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


def update_old_series(group, force_update):
    """Update a list/series in the old system
    :param group: EventGroup instance
    :param force_update: force the update even if the object is not new
    :return: OldSeries instance
    """
    if _old_talks_configured() and group:
        old_series, new_group = OldSeries.objects.get_or_create(group=group)
        if new_group:
            group_xml = group_to_old_series(group)
            group_url = "{server}/list/api_create".format(server=settings.OLD_TALKS_SERVER)
            response = requests.post(group_url, group_xml, auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                     allow_redirects=True, stream=False, headers={"Accept": "application/xml"})
            if response.status_code == 200:
                old_series.old_series_id = get_list_id(response.content)
                old_series.save()
            else:
                raise Exception(response.status_code)
        elif force_update:
            group_xml = group_to_old_series(group)
            group_url = "{server}/list/update/{id}".format(server=settings.OLD_TALKS_SERVER, id=old_series.old_series_id)
            response = requests.post(group_url, group_xml, auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                     allow_redirects=True, stream=False, headers={"Accept": "application/xml"})
            if not response.status_code == 200:
                # response is a redirection to an edit page so ignore the content...
                raise Exception(response.status_code)
        return old_series
    return None


def delete_old_talks(event):
    if _old_talks_configured():
        try:
            old_talk = OldTalk.objects.get(event=event)
            url = "{server}/talk/delete/{id}".format(server=settings.OLD_TALKS_SERVER,
                                                     id=old_talk.old_talk_id)

            logger.debug("POSTing delete request to {url}".format(url=url))

            response = requests.post(url, " ", auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                     allow_redirects=True, stream=False, headers={"Accept": "application/xml"})
        except OldTalk.DoesNotExist:
            logger.debug("Talk {slug} not ")


def _old_talks_configured():
    """Check if the configuration has all the expected settings for
    :return:
    """
    if hasattr(settings, "OLD_TALKS_SERVER") and hasattr(settings, "OLD_TALKS_USER") and hasattr(settings, "OLD_TALKS_PASSWORD"):
        if settings.OLD_TALKS_SERVER and settings.OLD_TALKS_USER and settings.OLD_TALKS_PASSWORD:
            return True
    logger.info("Old talks tasks missing one or more of the following SETTINGS: OLD_TALKS_SERVER, OLD_TALKS_USER, OLD_TALKS_PASSWORD")
    return False
