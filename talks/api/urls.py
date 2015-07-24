from django.conf.urls import patterns, url

from .views import (api_event_search_hal, suggest_user, api_create_person,
                    save_item, remove_item, get_event_group, suggest_person, api_event_search_ics,
                    api_event_get, api_event_get_ics, api_event_group_ics, api_event_group, suggest_event_group)


urlpatterns = patterns('',
    url(r'^series/id/(?P<event_group_id>\d+)', get_event_group, name='get-event-group'),
    url(r'^series/suggest$', suggest_event_group, name='api-event-group-suggest'),
    url(r'^series/(?P<event_group_slug>[^/]+).ics', api_event_group_ics, name='api-event-group-ics'),
    url(r'^series/(?P<event_group_slug>[^/]+)', api_event_group, name='api-event-group'),
    url(r'^talks/search$', api_event_search_hal, name='api-search-events'),
    url(r'^talks/search.ics$', api_event_search_ics, name='api-search-events-ics'),
    url(r'^talks/(?P<slug>[^/]+).ics$', api_event_get_ics, name='event-detail-ics'),
    url(r'^talks/(?P<slug>[^/]+)', api_event_get, name='event-detail'),
    url(r'^user/suggest$', suggest_user, name='api-user-suggest'),
    url(r'^persons/new$', api_create_person, name='api-person-create'),
    url(r'^persons/suggest$', suggest_person, name='api-person-suggest'),
    url(r'^collections/me/add$', save_item, name="save-item"),
    url(r'^collections/me/remove$', remove_item, name="remove-item"),
)

