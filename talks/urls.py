from django.conf.urls import patterns, include, url
from django.contrib import admin

from django_webauth.views import LoginView
from rest_framework import routers

from events.views import (homepage, upcoming_events, show_person, create_person, edit_person, show_event, edit_event, events_for_day,
                          events_for_month, events_for_year, create_event, list_event_groups,
                          create_event_group, show_event_group, edit_event_group, contributors_home, contributors_events,
                          contributors_eventgroups, contributors_persons, delete_event, delete_event_group, show_topic)
from talks.api.views import api_event_search
from talks.events_search.forms import DateFacetedSearchForm
from talks.events_search.views import SearchView
from talks.events_search.conf import sqs
from api.views import (EventViewSet, EventGroupViewSet, get_speaker, suggest_person, suggest_user, api_create_person,
                       save_item, remove_item, get_event_group)

from audit_trail.urls import urlpatterns as audit_urls

from users.views import webauth_logout

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'series', EventGroupViewSet)

urlpatterns = patterns('',
    # WebAuth login/logout
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', webauth_logout, name='logout'),

    url(r'^api/', include(router.urls)),
    url(r'^api/series/id/(?P<event_group_id>\d+)', get_event_group, name='get-event-group'),
    url(r'^api/events/search$', api_event_search, name='api-search-events'),
    url(r'^api/user/suggest$', suggest_user, name='suggest-user'),
    url(r'^api/persons/new$', api_create_person, name='api-create-person'),
    url(r'^api/speaker/(?P<person_slug_list>[^/]+)$', get_speaker, name='get-speaker'),

    url(r'^api/collections/me/add$', save_item, name="save-item"),
    url(r'^api/collections/me/remove$', remove_item, name="remove-item"),

    url(r'^search/', SearchView(form_class=DateFacetedSearchForm, searchqueryset=sqs, load_all=False), name='haystack_search'),
    url(r'^$', homepage, name='homepage'),
    url(r'^talks$', upcoming_events, name='upcoming_events'),
    url(r'^talks/persons/new$', create_person, name='create-person'),
    url(r'^talks/persons/suggest$', suggest_person, name='suggest-person'),
    url(r'^talks/persons/id/(?P<person_slug>[^/]+)$', show_person, name='show-person'),
    url(r'^talks/persons/id/(?P<person_slug>[^/]+)/edit$', edit_person, name='edit-person'),
    url(r'^talks/new$', create_event, name='create-event'),
    url(r'^talks/id/(?P<event_slug>[^/]+)/$', show_event, name='show-event'),
    url(r'^talks/id/(?P<event_slug>[^/]+)/edit$', edit_event, name='edit-event'),
    url(r'^talks/id/(?P<event_slug>[^/]+)/delete', delete_event, name='delete-event'),
    url(r'^talks/series/(?P<group_slug>[^/]+)/new$', create_event, name='create-event-in-group'),
    url(r'^talks/date/(?P<year>\d{4})/$', events_for_year, name='events_year'),
    url(r'^talks/date/(?P<year>\d{4})/(?P<month>\d{2})/$', events_for_month, name='events_month'),
    url(r'^talks/date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', events_for_day, name='events_day'),
    url(r'^talks/series/$', list_event_groups, name='list-event-groups'),
    url(r'^talks/series/new$', create_event_group, name='create-event-group'),
    url(r'^talks/series/id/(?P<event_group_slug>[^/]+)$', show_event_group, name='show-event-group'),
    url(r'^talks/series/id/(?P<event_group_slug>[^/]+)/edit$', edit_event_group, name='edit-event-group'),
    url(r'^talks/series/id/(?P<event_group_slug>[^/]+)/delete', delete_event_group, name='delete-event-group'),
    url(r'^talks/topics/id/$', show_topic, name="show-topic"),
    url(r'^contributors/$', contributors_home, name='contributors-home'),
    url(r'^contributors/talks$', contributors_events, name='contributors-events'),
    url(r'^contributors/series', contributors_eventgroups, name='contributors-eventgroups'),
    url(r'^contributors/persons$', contributors_persons, name='contributors-persons'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^audit/', include(audit_urls, namespace='audit'))

)
