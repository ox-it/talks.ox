from django.conf.urls import patterns, url

from .views import database_usage, revision_details


urlpatterns = patterns('audit',
    url(r'^$', database_usage, name='list'),
    url(r'^/(?P<revision_id>\d+)/$', revision_details, name='details'),
)
