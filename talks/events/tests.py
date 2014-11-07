import os
import unittest
import logging

import mock
import requests
from django.conf import settings
from django.test import TestCase
from django.core.cache.backends.base import BaseCache
from django.contrib.staticfiles.finders import find as find_static_file

from . import forms, models, factories, typeahead

VALID_DATE_STRING = "2014-05-12 12:18"


def intercept_requests_to_statics(url, *a, **k):
    """
    Utility function to use with mock.path.
    Blocks all requests through `requests.get` except for those to local static files.
    In that case makes `requests.get` return file content without going through `httplib`
    """
    logging.info("intercept: %s", url)
    if url.startswith(settings.STATIC_URL):
        r = requests.Response()
        try:
            path = url[len(settings.STATIC_URL):]
            path = path.split('?')[0]  # FIXME use urlparse
            file_path = find_static_file(path)
            logging.info("path:%r", path)
            logging.info("file+path:%r", file_path)
            if file_path and os.path.isfile(file_path):
                with open(file_path) as f:
                    r._content = f.read()
                    r.status_code = 200
                    logging.info("response: %s", r._content)
                    logging.info("response: %s", r.content)
            else:
                r.status_code = 404
        except Exception, e:
            r.status_code = 500
            r.reason = e.message
            import traceback
            r._content = traceback.format_exc()
        finally:
            logging.info("response: %s", r._content)
            return r
    raise AssertionError("External request detected: %s" % url)


def patch_requests():
    requests_patcher = mock.patch('requests.get', autospec=True)
    requests_get = requests_patcher.start()
    requests_get.side_effect = intercept_requests_to_statics
    return requests_patcher


def assert_not_called(mock):
    if mock.call_args is not None:
        raise AssertionError("Unexpected call to %s: %s\n" % (mock, mock.call_args))


class TestEventForm(TestCase):

    def test_empty(self):
        form = forms.EventForm({})
        self.assertEquals(form.is_valid(), False, "empty form should not validate")
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertEquals(len(errors), 6)
        self.assertIn('booking_type', errors)
        self.assertIn('audience', errors)
        self.assertIn('start', errors)
        self.assertIn('end', errors)
        self.assertIn('status', errors)
        self.assertIn('__all__', errors)

    def test_all_fields_blanked(self):
        data = {
            'description': u'',
            'title': u'',
            'location': u'',
            'department_suggest': u'',
            'start': u'',
            'topics': u'',
            'speaker_suggest': u'',
            'location_suggest': u'',
            'department_organiser': u'',
            'speakers': u'',
            'topic_suggest': u'',
            'end': u'',
        }
        form = forms.EventForm(data)
        self.assertEquals(form.is_valid(), False, "blanked form should not validate")
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertEquals(len(errors), 6)
        self.assertIn('booking_type', errors)
        self.assertIn('audience', errors)
        self.assertIn('status', errors)
        self.assertIn('start', errors)
        self.assertIn('end', errors)
        self.assertIn('__all__', errors)

    def test_invalid_date(self):
        data = {
            'description': u'',
            'title': u'',
            'title_not_announced': u'1',
            'location': u'',
            'department_suggest': u'',
            'start': u'94872394',
            'topics': u'',
            'speaker_suggest': u'',
            'location_suggest': u'',
            'department_organiser': u'',
            'speakers': u'',
            'booking_type': u'nr',
            'audience': u'public',
            'topic_suggest': u'',
            'status': models.EVENT_IN_PREPARATION,
            'end': VALID_DATE_STRING,
        }
        form = forms.EventForm(data)
        self.assertEquals(form.is_valid(), False, "blanked form should not validate")
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertIn('start', errors)
        self.assertEquals(len(errors), 1)

    def test_happy(self):
        data = {
            'description': u'',
            'title': u'',
            'title_not_announced': u'1',
            'location': u'',
            'department_suggest': u'',
            'start': VALID_DATE_STRING,
            'topics': u'',
            'speaker_suggest': u'',
            'location_suggest': u'',
            'department_organiser': u'',
            'speakers': u'',
            'booking_type': u'nr',
            'audience': u'public',
            'topic_suggest': u'',
            'status': models.EVENT_IN_PREPARATION,
            'end': VALID_DATE_STRING,
        }
        form = forms.EventForm(data)
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertTrue(form.is_valid(), "form should validate")

    def test_title_blank(self):
        data = {
            'title': '',
        }
        form = forms.EventForm(data)
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertIn('__all__', form.errors)
        self.assertIn("Either provide title or mark it as not announced", form.errors['__all__'])
        self.assertNotIn('title', form.errors)
        self.assertNotIn('title_not_announced', form.errors)

    def test_title_not_announced_false(self):
        data = {
            'title': 'something',
            'title_not_announced': 'false',
        }
        form = forms.EventForm(data)
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertNotIn("Either provide title or mark it as not announced", form.errors.get('__all__', []))
        self.assertNotIn('title', form.errors)
        self.assertNotIn('title_not_announced', form.errors)

    def test_title_not_announced_true_title_not_blank(self):
        data = {
            'title': 'something',
            'title_not_announced': 'true',
        }
        form = forms.EventForm(data)
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertNotIn("Either provide title or mark it as not announced", form.errors.get('__all__', []))
        self.assertNotIn('title', form.errors)
        self.assertNotIn('title_not_announced', form.errors)

    def test_title_not_announced_true_title_blank(self):
        data = {
            'title': '',
            'title_not_announced': 'true',
        }
        form = forms.EventForm(data)
        errors = form.errors.as_data()
        logging.info("form errors: %s", errors)
        self.assertNotIn("Either provide title or mark it as not announced", form.errors.get('__all__', []))
        self.assertNotIn('title', form.errors)
        self.assertNotIn('title_not_announced', form.errors)


class TestEventGroupForm(TestCase):

    def test_empty(self):
        form = forms.EventGroupForm({})
        self.assertEquals(form.is_valid(), False, "empty form should not validate")
        errors = form.errors.as_data()
        self.assertIn('title', errors)
        self.assertIn('description', errors)
        self.assertEquals(len(errors), 2)

    def test_all_fields_blanked(self):
        data = {
            'description': u'',
            'title': u'',
            'group_type': u'',
        }
        form = forms.EventGroupForm(data)
        self.assertEquals(form.is_valid(), False, "blanked form should not validate")
        errors = form.errors.as_data()
        self.assertIn('title', errors)
        self.assertIn('description', errors)
        self.assertEquals(len(errors), 2)

    def test_all_fields_valid(self):
        data = {
            'description': u'something',
            'title': u'some title',
            'group_type': u'SE',
        }
        form = forms.EventGroupForm(data)
        self.assertEquals(form.is_valid(), True, "form should validate")


class TestEventGroupViews(TestCase):
    def test_show_event_group_404(self):
        response = self.client.get("/events/groups/1")
        self.assertEquals(response.status_code, 404)

    def test_list_event_groups_empty(self):
        response = self.client.get("/events/groups/")
        self.assertEquals(response.status_code, 200)

    def test_list_event_groups_some(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/events/groups/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, group.title)

    def test_show_event_group_200(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/events/groups/id/%s" % group.id)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, group.title)
        self.assertContains(response, group.description)

    def test_edit_event_group_404(self):
        response = self.client.get("/events/groups/id/1/edit")
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, "events/event_group_form.html")

    def test_edit_event_group_200(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/events/groups/id/%s/edit" % group.id)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, group.title)
        self.assertContains(response, group.description)
        self.assertTemplateUsed(response, "events/event_group_form.html")

    def test_edit_event_group_post_happy(self):
        group = factories.EventGroupFactory.create()
        data = {
            'title': 'lkfjlfkds',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/events/groups/id/%s/edit" % group.id, data)
        self.assertRedirects(response, "/events/groups/id/%s" % group.id)
        saved_group = models.EventGroup.objects.get(pk=group.id)
        self.assertEquals(saved_group.title, data['title'])
        self.assertEquals(saved_group.description, data['description'])
        self.assertTemplateNotUsed(response, "events/event_group_form.html")

    def test_edit_event_group_post_invalid(self):
        old_title = 'some_old_title'
        old_description = 'old_description'
        group = factories.EventGroupFactory.create(
            title=old_title,
            description=old_description
        )
        data = {
            'title': '',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/events/groups/id/%s/edit" % group.id, data)
        saved_group = models.EventGroup.objects.get(pk=group.id)
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertEquals(saved_group.title, old_title)
        self.assertEquals(saved_group.description, old_description)
        self.assertTemplateUsed(response, "events/event_group_form.html")

    def test_create_event_group_200(self):
        response = self.client.get("/events/groups/new")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_group_form.html")

    def test_create_event_group_post_happy(self):
        data = {
            'title': 'lkfjlfkds',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/events/groups/new", data)
        saved_group = models.EventGroup.objects.get()
        self.assertRedirects(response, "/events/groups/id/%s" % saved_group.id)
        self.assertEquals(saved_group.title, data['title'])
        self.assertEquals(saved_group.description, data['description'])
        self.assertTemplateNotUsed(response, "events/event_group_form.html")

    def test_create_event_group_post_invalid(self):
        data = {
            'title': '',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/events/groups/new", data)
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertQuerysetEqual(models.EventGroup.objects.all(), [])
        self.assertTemplateUsed(response, "events/event_group_form.html")


class TestCreateEventView(TestCase):

    def test_get_happy_no_group_id(self):
        response = self.client.get('/events/new')
        logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_form.html')
        self.assertContains(response, "Oxford Talks")
        self.assertContains(response, "Add Talk")
        self.assertIn('event_form', response.context)
        self.assertIn('speaker_form', response.context)

    def test_get_nonexistent_group(self):
        response = self.client.get('/events/groups/8475623/new')
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, 'events/event_form.html')

    def test_get_happy_for_existing_group(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get('/events/groups/%s/new' % group.pk)
        logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertEquals(response.status_code, 200)
        self.assertIn('event_form', response.context)
        self.assertEquals(response.context['event_form']['group'].value(), group.pk)

    def test_post_valid_save_and_continue_no_group_id(self):
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        data = {
            'event-description': description,
            'another': u'true',
            'event-title': title,
            'event-location': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': [],
            'event-group-description': u'',
            'event-department_organiser': u'',
            'event-group-event_group_select': u'',
            'event-speakers': [],
            'event-group-group_type': u'',
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-group-select_create': u'CRE',
            'event-end': VALID_DATE_STRING,
            'event-group-title': u'',
            'name': u'',
            'event-booking_type': models.BOOKING_NOT_REQUIRED,
            'event-audience': models.AUDIENCE_PUBLIC,
            'event-status': models.EVENT_IN_PREPARATION,
        }

        response = self.client.post('/events/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, '/events/new')
        count = models.Event.objects.filter(title=title, description=description).count()
        self.assertEquals(count, 1, msg="Event instance was not saved")

    def test_post_valid_save_and_continue_with_group_id(self):
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        group = factories.EventGroupFactory.create()
        group_id = group.pk
        data = {
            'event-description': description,
            'another': u'true',
            'event-title': title,
            'event-location': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': [],
            'event-department_organiser': u'',
            'event-speakers': [],
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-topic_suggest': u'',
            'event-end': VALID_DATE_STRING,
            'event-group': unicode(group_id),
            'name': u'',
            'event-booking_type': models.BOOKING_NOT_REQUIRED,
            'event-audience': models.AUDIENCE_PUBLIC,
            'event-status': models.EVENT_IN_PREPARATION,
        }

        response = self.client.post('/events/groups/%s/new' % group_id, data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, '/events/groups/%s/new' % group_id)
        count = models.Event.objects.filter(title=title, description=description, group_id=group_id).count()
        logging.info("events:%s", models.Event.objects.all())
        self.assertEquals(count, 1, msg="Event instance was not saved")

    @mock.patch('requests.get', autospec=True)
    def test_post_valid(self, requests_get):
        requests_get.return_value.json.return_value = {'_embedded': {'pois': []}}
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        data = {
            'event-description': description,
            'event-title': title,
            'event-group': u'',
            'event-location': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': [],
            'event-speakers': [],
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-department_organiser': u'',
            'event-end': VALID_DATE_STRING,
            'name': u'',
            'event-booking_type': models.BOOKING_REQUIRED,
            'event-audience': models.AUDIENCE_OXFORD,
            'event-status': models.EVENT_IN_PREPARATION,
        }
        response = self.client.post('/events/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors.as_data())
        try:
            event = models.Event.objects.get(title=title, description=description)
        except models.Event.DoesNotExist:
            self.fail("Event instance was not saved")
        self.assertRedirects(response, event.get_absolute_url())
        self.assertEquals(event.title, data['event-title'])
        self.assertEquals(event.description, data['event-description'])
        self.assertEquals(event.booking_type, data['event-booking_type'])
        self.assertEquals(event.audience, data['event-audience'])

    @mock.patch('requests.get', autospec=True)
    def test_post_valid_with_speakers(self, requests_get):
        requests_get.return_value.json.return_value = {'_embedded': {'pois': []}}
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        speakers = factories.PersonFactory.create_batch(3)
        data = {
            'event-description': description,
            'event-title': title,
            'event-group': u'',
            'event-location': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': [],
            'event-department_organiser': u'',
            'event-speakers': [str(s.pk) for s in speakers],
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-end': VALID_DATE_STRING,
            'name': u'',
            'event-booking_type': models.BOOKING_NOT_REQUIRED,
            'event-audience': models.AUDIENCE_PUBLIC,
            'event-status': models.EVENT_IN_PREPARATION,
        }
        response = self.client.post('/events/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        try:
            event = models.Event.objects.get(title=title, description=description)
        except models.Event.DoesNotExist:
            self.fail("Event instance was not saved")
        logging.info("event.speakers: %s", event.speakers)
        self.assertEquals(set(speakers), set(event.speakers), "speakers were not assigned properly")
        self.assertRedirects(response, event.get_absolute_url())

    @mock.patch('requests.get', autospec=True)
    def test_post_valid_with_topics(self, requests_get):
        requests_get.return_value.json.return_value = {'_embedded': {'pois': [], 'concepts': []}},
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        topics = factories.TopicItemFactory.create_batch(3)
        data = {
            'event-description': description,
            'event-title': title,
            'event-group': u'',
            'event-location': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': [t.uri for t in topics],
            'event-department_organiser': u'',
            'event-speakers': [],
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-end': VALID_DATE_STRING,
            'name': u'',
            'event-booking_type': models.BOOKING_NOT_REQUIRED,
            'event-audience': models.AUDIENCE_PUBLIC,
            'event-status': models.EVENT_IN_PREPARATION,
        }

        response = self.client.post('/events/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        try:
            event = models.Event.objects.get(title=title, description=description)
        except models.Event.DoesNotExist:
            self.fail("Event instance was not saved")
        logging.info("event.topics: %s", [t.uri for t in event.topics.all()])
        self.assertEquals({t.uri for t in topics}, {t.uri for t in event.topics.all()}, "topics were not assigned properly")
        self.assertRedirects(response, event.get_absolute_url())


class TestEditEventView(TestCase):
    def test_edit_event_404(self):
        response = self.client.get("/events/id/1/edit")
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, "events/event_form.html")

    def test_edit_event_200(self):
        event = factories.EventFactory.create()
        response = self.client.get("/events/id/%s/edit" % event.id)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, event.title)
        self.assertContains(response, event.description)
        self.assertContains(response, event.start)
        self.assertContains(response, event.end)
        self.assertTemplateUsed(response, "events/event_form.html")

    @mock.patch('requests.get', autospec=True)
    def test_edit_event_post_happy(self, requests_get):
        requests_get.return_value.json.return_value = {'_embedded': {'pois': []}}
        event = factories.EventFactory.create()
        data = {
            'event-title': 'lkfjlfkds',
            'event-description': 'dflksfoingf',
            'event-group_type': '',
            'event-booking_type': models.BOOKING_REQUIRED,
            'event-audience': models.AUDIENCE_OXFORD,
            'event-status': models.EVENT_IN_PREPARATION,
            'event-start': VALID_DATE_STRING,
            'event-end': VALID_DATE_STRING
        }

        response = self.client.post("/events/id/%s/edit" % event.id, data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, "/events/id/%s" % event.id)
        saved_event = models.Event.objects.get(pk=event.id)
        self.assertEquals(saved_event.title, data['event-title'])
        self.assertEquals(saved_event.description, data['event-description'])
        self.assertEquals(saved_event.booking_type, data['event-booking_type'])
        self.assertEquals(saved_event.audience, data['event-audience'])
        self.assertTemplateNotUsed(response, "events/event_form.html")

    def test_edit_event_post_invalid(self):
        old_title = u'some_old_title'
        old_description = u'old_description'
        event = factories.EventFactory.create(
            title=old_title,
            description=old_description,
        )
        data = {
            'event-title': '',
            'event-description': 'dflksfoingf',
        }

        response = self.client.post("/events/id/%s/edit" % event.id, data)
        saved_event = models.Event.objects.get(pk=event.id)
        self.assertEquals(response.status_code, 200)
        logging.info("form errors: %s", response.context['event_form'].errors.as_data())
        self.assertFormError(response, 'event_form', 'booking_type', ['This field is required.'])
        self.assertFormError(response, 'event_form', 'audience', ['This field is required.'])
        self.assertEquals(saved_event.title, old_title)
        self.assertEquals(saved_event.description, old_description)
        self.assertTemplateUsed(response, "events/event_form.html")


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
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None)
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
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None)
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
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None)
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
        get_objects_from_response.assert_called_once_with(requests_get.return_value, None)
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
        forms.LOCATION_DATA_SOURCE.cache.clear()

        result = forms.LOCATION_DATA_SOURCE.get_object_by_id(location_id)
        result_from_cache = forms.LOCATION_DATA_SOURCE.get_object_by_id(location_id)

        self.assertEquals(result, location_object)
        self.assertEquals(result, result_from_cache)

    def test_department(self, requests_get):
        department_id = str(mock.sentinel.department_id)
        department_object = {'id': department_id, 'name': str(mock.sentinel.department_name)}
        requests_get.return_value = mock.Mock(spec=requests.Response)
        requests_get.return_value.json.return_value = {'_embedded': {'pois': [department_object]}}
        forms.DEPARTMENT_DATA_SOURCE.cache.clear()

        result = forms.DEPARTMENT_DATA_SOURCE.get_object_by_id(department_id)
        result_from_cache = forms.DEPARTMENT_DATA_SOURCE.get_object_by_id(department_id)

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
        forms.TOPICS_DATA_SOURCE.cache.clear()

        result = forms.TOPICS_DATA_SOURCE.get_object_by_id(topic_id)
        result_from_cache = forms.TOPICS_DATA_SOURCE.get_object_by_id(topic_id)

        self.assertEquals(result, topic_object)
        self.assertEquals(result, result_from_cache)

    def test_persons(self, requests_get):
        persons = factories.PersonFactory.create_batch(3)
        person = persons[1]

        result = forms.SPEAKERS_DATA_SOURCE.get_object_by_id(person.id)

        assert_not_called(requests_get)

        self.assertEquals(result['id'], person.id)
        self.assertEquals(result['name'], person.name)
