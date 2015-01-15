from django.conf.urls import patterns, url

from talks.contributors.views import (contributors_home, contributors_events,
                                      contributors_eventgroups, contributors_persons)

urlpatterns = patterns('',
    url(r'^$', contributors_home, name='contributors-home'),
    url(r'^talks$', contributors_events, name='contributors-events'),
    url(r'^series', contributors_eventgroups, name='contributors-eventgroups'),
    url(r'^persons$', contributors_persons, name='contributors-persons'),
)
