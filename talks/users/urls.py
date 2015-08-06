from django.conf.urls import patterns, url

from talks.users.views import (manage_collections, list_public_collections, view_collection, add_collection, edit_collection, delete_collection)


urlpatterns = patterns('',
    url(r'^lists$', manage_collections, name='manage-lists'),
    url(r'^lists/public$', list_public_collections, name='manage-public-lists'),
    url(r'^lists/new$', add_collection, name='add-list'),
    url(r'^lists/id/(?P<collection_slug>[^/]+)/$', view_collection, name='view-list'),
    url(r'^lists/id/(?P<collection_slug>[^/]+)/edit$', edit_collection, name='edit-list'),
    url(r'^lists/id/(?P<collection_slug>[^/]+)/delete', delete_collection, name='delete-list'),
)
