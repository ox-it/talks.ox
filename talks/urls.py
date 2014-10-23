from django.conf.urls import patterns, include, url
from django.contrib import admin

from django_webauth.views import LoginView

from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from rest_framework import routers

from events.views import (homepage, upcoming_events, event, events_for_day,
                          events_for_month, events_for_year, create_event,
                          create_event_group, show_event_group, edit_event_group)

from api.views import (EventViewSet, create_speaker, suggest_speaker,
                       save_item, remove_item)

from users.views import webauth_logout

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)

sqs = SearchQuerySet().facet('speakers', mincount=1).facet('locations', mincount=1).facet('topics', mincount=1)
# .date_facet('start', date(2014,1,1), date(2015,1,1), 'month')   removed for now as we want dynamic dates and range


urlpatterns = patterns('',
    # WebAuth login/logout
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', webauth_logout, name='logout'),

    url(r'^api/', include(router.urls)),
    url(r'^api/collections/me/add$', save_item, name="save-item"),
    url(r'^api/collections/me/remove$', remove_item, name="remove-item"),
    url(r'^search/', FacetedSearchView(form_class=FacetedSearchForm, searchqueryset=sqs, load_all=False), name='haystack_search'),
    url(r'^$', homepage, name='homepage'),
    url(r'^events$', upcoming_events, name='upcoming_events'),
    url(r'^events/speakers/new$', create_speaker, name='create-speaker'),
    url(r'^events/speakers/suggest$', suggest_speaker, name='suggest-speaker'),
    url(r'^events/new$', create_event, name='create-event'),
    url(r'^events/groups/(?P<group_id>\d+)/new$', create_event, name='create-event-in-group'),
    url(r'^events/id/(?P<event_id>\d+)$', event, name='event'),
    url(r'^events/date/(?P<year>\d{4})/$', events_for_year, name='events_year'),
    url(r'^events/date/(?P<year>\d{4})/(?P<month>\d{2})/$', events_for_month, name='events_month'),
    url(r'^events/date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', events_for_day, name='events_day'),
    url(r'^events/groups/new$', create_event_group, name='create-event-group'),
    url(r'^events/groups/id/(?P<event_group_id>\d+)$', show_event_group, name='show-event-group'),
    url(r'^events/groups/id/(?P<event_group_id>\d+)/edit$', edit_event_group, name='edit-event-group'),
    url(r'^admin/', include(admin.site.urls)),
)
