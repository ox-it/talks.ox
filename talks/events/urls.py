from django.conf.urls import patterns, url

from talks.events.views import (upcoming_events, show_person, show_event, events_for_day, show_department_organiser,
                                events_for_month, events_for_year, list_event_groups,show_event_group, show_topic,
                                show_department_descendant)
from talks.contributors.views import (create_person, edit_person, edit_event, create_event, create_event_group,
                                      edit_event_group, delete_event, delete_event_group)


urlpatterns = patterns('',
    url(r'^$', upcoming_events, name='upcoming_events'),
    url(r'^persons/new$', create_person, name='create-person'),
    url(r'^persons/id/(?P<person_slug>[^/]+)$', show_person, name='show-person'),
    url(r'^persons/id/(?P<person_slug>[^/]+)/edit$', edit_person, name='edit-person'),
    url(r'^new$', create_event, name='create-event'),
    url(r'^id/(?P<event_slug>[^/]+)/$', show_event, name='show-event'),
    url(r'^id/(?P<event_slug>[^/]+)/edit$', edit_event, name='edit-event'),
    url(r'^id/(?P<event_slug>[^/]+)/delete', delete_event, name='delete-event'),
    url(r'^series/(?P<group_slug>[^/]+)/new$', create_event, name='create-event-in-group'),
    url(r'^date/(?P<year>\d{4})/$', events_for_year, name='events_year'),
    url(r'^date/(?P<year>\d{4})/(?P<month>\d{2})/$', events_for_month, name='events_month'),
    url(r'^date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', events_for_day, name='events_day'),
    url(r'^series/$', list_event_groups, name='list-event-groups'),
    url(r'^series/new$', create_event_group, name='create-event-group'),
    url(r'^series/id/(?P<event_group_slug>[^/]+)$', show_event_group, name='show-event-group'),
    url(r'^series/id/(?P<event_group_slug>[^/]+)/edit$', edit_event_group, name='edit-event-group'),
    url(r'^series/id/(?P<event_group_slug>[^/]+)/delete', delete_event_group, name='delete-event-group'),
    url(r'^topics/id/$', show_topic, name="show-topic"),
    url(r'^department/id/(?P<org_id>[^/]+)$', show_department_organiser, name="show-department"),
    url(r'^department/id/(?P<org_id>[^/]+)/descendants$', show_department_descendant, name="show-department"),
)
