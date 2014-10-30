import logging

import requests
from django.conf import settings

from talks.old_talks.models import (OldTalk, OldSeries, event_to_old_talk,
                                    get_list_id, group_to_old_series)

logger = logging.getLogger(__name__)


def update_old_talks(event):
    if hasattr(settings, "OLD_TALKS_SERVER") and hasattr(settings, "OLD_TALKS_USER") and hasattr(settings, "OLD_TALKS_PASSWORD"):
        if event.group:
            old_series, new_group = OldSeries.objects.get_or_create(group=event.group)
            if new_group:
                group = group_to_old_series(event.group)

                group_url = "{server}/list/api_create".format(server=settings.OLD_TALKS_SERVER)
                response = requests.post(group_url, group, auth=(settings.OLD_TALKS_USER, settings.OLD_TALKS_PASSWORD),
                                         allow_redirects=True, stream=False, headers={"Accept": "application/xml"})
                if response.status_code == 200:
                    old_series.old_series_id = get_list_id(response.content)
                    old_series.save()
                else:
                    raise Exception(response.status_code)
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