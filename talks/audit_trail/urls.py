from django.conf.urls import url

from .views import database_usage, revision_details


urlpatterns = [
    url(r'^$', database_usage, name='audit.list'),
    url(r'^(?P<revision_id>\d+)/$', revision_details, name='audit.details'),
]
