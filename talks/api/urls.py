from django.conf.urls import patterns, include, url

from rest_framework import routers
from rest_framework.routers import Route

from .views import (api_event_search, EventViewSet, EventGroupViewSet, suggest_user, api_create_person,
                    save_item, remove_item, get_event_group, suggest_person)

class TalksAPIRouter(routers.DefaultRouter):
    """
    Custom router which is read only, and only provides the retrieve endpoint, not the lists or
    """
    routes = [
        Route(
            url=r'{prefix}/{lookup}$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            initkwargs={'suffix': 'Detail'}
        ),
    ]

router = TalksAPIRouter()
router.register(r'events', EventViewSet)
router.register(r'series', EventGroupViewSet)

urlpatterns = patterns('',
    url(r'^series/id/(?P<event_group_id>\d+)', get_event_group, name='get-event-group'),
    url(r'^events/search$', api_event_search, name='api-search-events'),
    url(r'^user/suggest$', suggest_user, name='api-user-suggest'),
    url(r'^persons/new$', api_create_person, name='api-person-create'),
    url(r'^persons/suggest$', suggest_person, name='api-person-suggest'),
    url(r'^collections/me/add$', save_item, name="save-item"),
    url(r'^collections/me/remove$', remove_item, name="remove-item"),
    url(r'^', include(router.urls)),    # comes last to avoid events/search being treated as a slug
)
