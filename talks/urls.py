from collections import OrderedDict
from django.conf.urls import patterns, include, url
from django.contrib import admin
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet

from rest_framework import routers

from events.views import (homepage, upcoming_events, event, events_for_day,
                          events_for_month, events_for_year, create_event,
                          event_group, SearchView)

from api.views import (EventViewSet, create_speaker, suggest_speaker,
                       save_item, remove_item)

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)

# Order used in the search UI for the filtering per start date
FACET_START_DATE = OrderedDict()
FACET_START_DATE['Next 7 days'] = {'solr_query': '[NOW TO NOW/DAY+7DAY]', 'url_param': 'next_7'}
FACET_START_DATE['Future talks'] = {'solr_query': '[NOW/DAY+7DAY TO *]', 'url_param': 'future'}
FACET_START_DATE['Past talks'] = {'solr_query': '[* TO NOW]', 'url_param': 'past'}

# map an URL param to a solr query, used when a search is done
URL_TO_SOLR = {d['url_param']: d['solr_query'] for d in FACET_START_DATE.itervalues()}

# solr query to "user-friendly" name
SOLR_TO_NAME = {d['solr_query']: key for key, d in FACET_START_DATE.iteritems()}

sqs = (SearchQuerySet()
       .facet('speakers', mincount=1).facet('locations', mincount=1).facet('topics', mincount=1))

# add all the facet start date queries to the queryset
for v in FACET_START_DATE.itervalues():
    sqs = sqs.query_facet('start', v['solr_query'])

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^search/', SearchView(form_class=FacetedSearchForm, searchqueryset=sqs, load_all=False), name='haystack_search'),
    url(r'^api/collections/me/add$', save_item, name="save-item"),
    url(r'^api/collections/me/remove$', remove_item, name="remove-item"),
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
    url(r'^events/groups/id/(?P<event_group_id>\d+)$', event_group, name='event-group'),
    url(r'^admin/', include(admin.site.urls)),
)
