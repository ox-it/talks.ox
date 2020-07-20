from __future__ import absolute_import
import unittest
import datetime
import mock
import requests

from django.test import TestCase
from django.core.cache.backends.base import BaseCache
from django.contrib.auth.models import User
from django.utils import timezone

from . import models, factories, typeahead, datasources
from talks.events.models import EVENT_PUBLISHED


def assert_not_called(mock):
    if mock.call_args is not None:
        raise AssertionError("Unexpected call to %s: %s\n" % (mock, mock.call_args))


class TestEventProperties(TestCase):

    def test_is_published(self):
        event = factories.EventFactory.create()
        event.embargo = True
        event.status = EVENT_PUBLISHED
        self.assertFalse(event.is_published)
        event.embargo = False
        self.assertTrue(event.is_published)

    def test_already_started(self):
        old_event = factories.EventFactory.create()
        old_event.start = timezone.now() - datetime.timedelta(days=1)
        self.assertTrue(old_event.already_started)
        new_event = factories.EventFactory.create()
        new_event.start = timezone.now() + datetime.timedelta(days=1)
        self.assertFalse(new_event.already_started)
        current_event = factories.EventFactory.create()
        current_event.start = timezone.now() - datetime.timedelta(minutes=30)
        current_event.end = timezone.now() + datetime.timedelta(minutes=30)
        self.assertTrue(current_event.already_started)

    def test_user_can_edit(self):
        superuser = User.objects.create_superuser("superuser", password="password", email="superuser@users.com")
        contrib_user = User.objects.create_user("contrib_user", password="password")
        contrib_user_editor = User.objects.create_user("contrib_user_editor", password="password")
        event = factories.EventFactory.create()
        event.editor_set.add(contrib_user_editor)
        self.assertTrue(event.user_can_edit(superuser))
        self.assertTrue(event.user_can_edit(contrib_user_editor))
        self.assertFalse(event.user_can_edit(contrib_user))


class TestEventPublishWorkflow(TestCase):

    def setUp(self):
        self.published = factories.EventFactory.create(status=models.EVENT_PUBLISHED)
        self.draft = factories.EventFactory.create(status=models.EVENT_IN_PREPARATION)
        self.embargo = factories.EventFactory.create(status=models.EVENT_IN_PREPARATION,
                                                     embargo=True)

    def test_published_manager(self):
        events = models.Event.published.all()
        self.assertEquals(len(events), 1)
        self.assertEquals(events[0], self.published)


@mock.patch('talks.events.typeahead.get_objects_from_response', autospec=True)
@mock.patch.object(typeahead.DataSource, 'cache', spec=BaseCache)
@mock.patch('requests.get', autospec=True)
class TestDataSourceFetchObjects(unittest.TestCase):

    def test_empty_id_list(self, requests_get, cache, get_objects_from_response):
        cache.get_many.return_value = {}
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url)
        result = ds._fetch_objects([])

        cache.get_many.assert_called_once_with([])
        assert_not_called(cache.set_many)
        assert_not_called(requests_get)
        assert_not_called(get_objects_from_response)
        self.assertEquals(result, {})

    def test_no_prefetch_url(self, requests_get, cache, get_objects_from_response):
        cache.get_many.return_value = {}

        ds = typeahead.DataSource(mock.sentinel.cache_key)
        with self.assertRaises(AttributeError) as e:
            ds._fetch_objects([mock.sentinel.id])

        cache.get_many.assert_called_once_with([mock.sentinel.id])
        self.assertEquals(e.exception.message, "'DataSource' object has no attribute 'get_prefetch_url'")
        assert_not_called(requests_get)
        assert_not_called(get_objects_from_response)

    def test_fetched_from_remote(self, requests_get, cache, get_objects_from_response):
        id_key = mock.sentinel.id_key
        fetched_id = mock.sentinel.id
        fetched_object = {id_key: fetched_id, 'foo': mock.sentinel.remaining_data}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        cache.get_many.return_value = {}
        get_objects_from_response.return_value = [fetched_object]
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url, id_key=id_key)
        result = ds._fetch_objects([fetched_id])

        cache.get_many.assert_called_once_with([fetched_id])
        cache.set_many.assert_called_once_with({fetched_id: fetched_object})
        requests_get.assert_called_once_with(mock.sentinel.url)
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None, False)
        self.assertEquals(result, {fetched_id: fetched_object})

    def test_fetched_from_cache(self, requests_get, cache, get_objects_from_response):
        cache.get_many.return_value = {mock.sentinel.id: mock.sentinel.object}
        get_prefetch_url = mock.Mock()

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url)
        result = ds._fetch_objects([mock.sentinel.id])

        cache.get_many.assert_called_once_with([mock.sentinel.id])
        assert_not_called(cache.set_many)
        assert_not_called(requests_get)
        assert_not_called(get_prefetch_url)
        assert_not_called(get_objects_from_response)
        self.assertEquals(result, {mock.sentinel.id: mock.sentinel.object})

    def test_fetched_from_cache_no_prefetch_url(self, requests_get, cache, get_objects_from_response):
        cache.get_many.return_value = {mock.sentinel.id: mock.sentinel.object}

        ds = typeahead.DataSource(mock.sentinel.cache_key)
        result = ds._fetch_objects([mock.sentinel.id])

        cache.get_many.assert_called_once_with([mock.sentinel.id])
        assert_not_called(cache.set_many)
        assert_not_called(requests_get)
        assert_not_called(get_objects_from_response)
        self.assertEquals(result, {mock.sentinel.id: mock.sentinel.object})

    def test_remote_not_found_in_response(self, requests_get, cache, get_objects_from_response):
        requests_get.return_value = mock.Mock(spec=requests.Response)
        cache.get_many.return_value = {}
        get_objects_from_response.return_value = {}
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url)
        result = ds._fetch_objects([mock.sentinel.id])

        cache.get_many.assert_called_once_with([mock.sentinel.id])
        assert_not_called(cache.set_many)
        assert_not_called(cache.set_many)
        requests_get.assert_called_once_with(mock.sentinel.url)
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None, False)
        self.assertEquals(result, {})

    def test_remote_404(self, requests_get, cache, get_objects_from_response):
        requests_get.return_value = requests.Response()
        requests_get.return_value.status_code = 404
        cache.get_many.return_value = {}
        get_objects_from_response.return_value = {}
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url)
        with self.assertRaises(requests.HTTPError) as e:
            ds._fetch_objects([mock.sentinel.id])

        self.assertEqual(e.exception.response.status_code, 404)

        assert_not_called(cache.set_many)
        requests_get.assert_called_once_with(mock.sentinel.url)
        assert_not_called(get_objects_from_response)

    def test_fetched_from_remote_and_cache(self, requests_get, cache, get_objects_from_response):
        id_key = mock.sentinel.id_key
        cached_id, cached_object = mock.sentinel.cached_id, mock.sentinel.cached_object
        fetched_id, fetched_object = mock.sentinel.fetched_id, {id_key: mock.sentinel.fetched_id}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        cache.get_many.return_value = {cached_id: cached_object}
        get_objects_from_response.return_value = [fetched_object]
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url, id_key=id_key)
        result = ds._fetch_objects([cached_id, fetched_id])

        cache.get_many.assert_called_once_with([cached_id, fetched_id])
        cache.set_many.assert_called_once_with({fetched_id: fetched_object})
        requests_get.assert_called_once_with(mock.sentinel.url)
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None, False)
        self.assertEquals(result, {
            cached_id: cached_object,
            fetched_id: fetched_object
        })

    def test_remote_returns_more_than_requested(self, requests_get, cache, get_objects_from_response):
        id_key = mock.sentinel.id_key
        fetched_id = mock.sentinel.id
        fetched_object = {id_key: fetched_id, 'foo': mock.sentinel.remaining_data}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        cache.get_many.return_value = {}
        get_objects_from_response.return_value = [fetched_object, {id_key: 'extra object'}]
        get_prefetch_url = mock.Mock(return_value=mock.sentinel.url)

        ds = typeahead.DataSource(mock.sentinel.cache_key, get_prefetch_url=get_prefetch_url, id_key=id_key)
        result = ds._fetch_objects([fetched_id])

        cache.get_many.assert_called_once_with([fetched_id])
        cache.set_many.assert_called_once_with({fetched_id: fetched_object})
        requests_get.assert_called_once_with(mock.sentinel.url)
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None, False)
        self.assertEquals(result, {fetched_id: fetched_object})


@mock.patch('talks.events.typeahead.DataSource._fetch_objects', autospec=True)
class TestDataSourceGetObjectById(unittest.TestCase):
    def test_not_found(self, fetch_objects):
        fetch_objects.return_value = {}

        ds = typeahead.DataSource(mock.sentinel.cache_key)
        result = ds.get_object_by_id(mock.sentinel.id)

        self.assertEquals(result, None)
        fetch_objects.assert_called_with(ds, [mock.sentinel.id])

    def test_found(self, fetch_objects):
        fetch_objects.return_value = {mock.sentinel.id: mock.sentinel.object}

        ds = typeahead.DataSource(mock.sentinel.cache_key)
        result = ds.get_object_by_id(mock.sentinel.id)

        self.assertEquals(result, mock.sentinel.object)
        fetch_objects.assert_called_with(ds, [mock.sentinel.id])


class TestGetObjectsFromResponse(unittest.TestCase):
    def test_no_filter(self):
        response = mock.Mock(spec=requests.Response)
        response.json.return_value = mock.sentinel.response_json
        expression = None

        result = typeahead.get_objects_from_response(response, expression)

        self.assertEquals(result, mock.sentinel.response_json)

    def test_noop_filter(self):
        response = mock.Mock(spec=requests.Response)
        response.json.return_value = mock.sentinel.response_json
        expression = 'response'

        result = typeahead.get_objects_from_response(response, expression)

        self.assertEquals(result, mock.sentinel.response_json)

    def test_property(self):
        response = mock.Mock(spec=requests.Response)
        response.json.return_value = {'foo': mock.sentinel.objects}
        expression = 'response.foo'

        result = typeahead.get_objects_from_response(response, expression)

        self.assertEquals(result, mock.sentinel.objects)

    def test_nested_property(self):
        response = mock.Mock(spec=requests.Response)
        response.json.return_value = {
            'foo': {
                'bar': mock.sentinel.objects,
                'baz': mock.sentinel.booby_trap,
            },
            'moo': mock.sentinel.invalid,
        }
        expression = 'response.foo.bar'

        result = typeahead.get_objects_from_response(response, expression)

        self.assertEquals(result, mock.sentinel.objects)

    def test_key_error(self):
        response = mock.Mock(spec=requests.Response)
        response.json.return_value = {}
        expression = 'response.foo'

        with self.assertRaises(KeyError) as e:
            typeahead.get_objects_from_response(response, expression)

        self.assertEquals(e.exception.message, 'foo')


@mock.patch('requests.get', autospec=True)
class TestDeclaredDataSources(unittest.TestCase):
    def test_location(self, requests_get):
        location_id = str(mock.sentinel.location_id)
        location_object = {'id': location_id, 'name': str(mock.sentinel.location_name)}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        requests_get.return_value.json.return_value = {'_embedded': {'pois': [location_object]}}
        datasources.LOCATION_DATA_SOURCE.cache.clear()

        result = datasources.LOCATION_DATA_SOURCE.get_object_by_id(location_id)
        result_from_cache = datasources.LOCATION_DATA_SOURCE.get_object_by_id(location_id)

        self.assertEquals(result, location_object)
        self.assertEquals(result, result_from_cache)

    def test_department(self, requests_get):
        department_id = str(mock.sentinel.department_id)
        department_object = {'id': department_id, 'name': str(mock.sentinel.department_name)}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        requests_get.return_value.json.return_value = {'_embedded': {'pois': [department_object]}}
        datasources.DEPARTMENT_DATA_SOURCE.cache.clear()

        result = datasources.DEPARTMENT_DATA_SOURCE.get_object_by_id(department_id)
        result_from_cache = datasources.DEPARTMENT_DATA_SOURCE.get_object_by_id(department_id)

        self.assertEquals(result, department_object)
        self.assertEquals(result, result_from_cache)

    def test_topics(self, requests_get):
        topic_id = str(mock.sentinel.topic_id)
        topic_object = {'uri': topic_id, 'prefLabel': str(mock.sentinel.topic_label)}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        requests_get.return_value.json.return_value = {
            '_embedded': {
                'concepts': [topic_object],
            },
        }
        datasources.TOPICS_DATA_SOURCE.cache.clear()

        result = datasources.TOPICS_DATA_SOURCE.get_object_by_id(topic_id)
        result_from_cache = datasources.TOPICS_DATA_SOURCE.get_object_by_id(topic_id)

        self.assertEquals(result, topic_object)
        self.assertEquals(result, result_from_cache)

    def test_persons(self, requests_get):
        persons = factories.PersonFactory.create_batch(3)
        person = persons[1]

        result = datasources.PERSONS_DATA_SOURCE.get_object_by_id(person.id)

        assert_not_called(requests_get)

        self.assertEquals(result['id'], person.id)
        self.assertEquals(result['name'], person.name)
