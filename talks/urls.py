from django.conf.urls import patterns, include, url
from django.contrib import admin

from events.views import (homepage, upcoming_events, event, events_for_day,
                          events_for_month, events_for_year)


urlpatterns = patterns('',
    url(r'^$', homepage, name='homepage'),
    url(r'^events$', upcoming_events, name='upcoming_events'),
    url(r'^events/id/(?P<event_id>\d+)$', event, name='event'),
    url(r'^events/date/(?P<year>\d{4})/$', events_for_year, name='events_year'),
    url(r'^events/date/(?P<year>\d{4})/(?P<month>\d{2})/$', events_for_month, name='events_month'),
    url(r'^events/date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', events_for_day, name='events_day'),
    url(r'^admin/', include(admin.site.urls)),
)
