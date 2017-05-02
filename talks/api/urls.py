from django.conf.urls import patterns, url

from .views import (api_event_search_hal, api_event_search_ics, api_event_get, api_event_get_ics,
                    api_event_group, get_event_group, suggest_event_group, api_event_group_ics,
                    suggest_user, suggest_user_by_complete_email_address, api_person, api_person_ics, suggest_person, api_create_person,
                    save_item, remove_item, subscribe_to_list, unsubscribe_from_list, api_collection, api_collection_ics,
                    suggest_talksuser_by_complete_email_address)


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
    url(r'^user/suggest/exact$', suggest_user_by_complete_email_address, name='api-user-suggest-exact'),
    url(r'^talksuser/suggest/exact$', suggest_talksuser_by_complete_email_address, name='api-talksuser-suggest-exact'),
    url(r'^persons/new$', api_create_person, name='api-person-create'),
    url(r'^persons/suggest$', suggest_person, name='api-person-suggest'),
    url(r'^person/(?P<person_slug>[^/]+).ics', api_person_ics, name='api-person-ics'),
    url(r'^person/(?P<person_slug>[^/]+)', api_person, name='api-person'),
    url(r'^collections/add-item$', save_item, name="save-item"),
    url(r'^collections/remove-item$', remove_item, name="remove-item"),
    url(r'^collections/subscribe$', subscribe_to_list, name="subscribe-to-list"),
    url(r'^collections/unsubscribe$', unsubscribe_from_list, name="unsubscribe-from-list"),
    url(r'^collections/id/(?P<collection_slug>[^/]+).ics', api_collection_ics, name='api-collection-ics'),
    url(r'^collections/id/(?P<collection_slug>[^/]+)', api_collection, name='api-collection'),
)
