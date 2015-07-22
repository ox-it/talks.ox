from django.conf.urls import patterns, include, url
from django.contrib import admin

from django_webauth.views import LoginView

from talks.events.views import (homepage, browse_events)
from talks.events_search.forms import DateFacetedSearchForm
from talks.events_search.views import SearchView
from talks.events_search.conf import sqs

from talks.api.urls import urlpatterns as api_urls
from talks.contributors.urls import urlpatterns  as contributors_urls
from talks.audit_trail.urls import urlpatterns as audit_urls
from talks.events.urls import urlpatterns as events_urls
from talks.users.views import webauth_logout
from talks.core.healthchecks import healthcheck


urlpatterns = patterns('',
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', webauth_logout, name='logout'),

    url(r'^search/', SearchView(form_class=DateFacetedSearchForm, searchqueryset=sqs, load_all=False),
        name='haystack_search'),
    url(r'^$', homepage, name='homepage'),
    url(r'^browse$', browse_events, name='browse_events'),
    url(r'^talks/', include(events_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^audit/', include(audit_urls, namespace='audit')),
    url(r'^api/', include(api_urls)),
    url(r'^contributors/', include(contributors_urls)),
    url(r'^_health$', healthcheck, name='healthcheck')
)
