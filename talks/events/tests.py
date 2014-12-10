import unittest
import logging
import datetime
import mock
import requests

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.cache.backends.base import BaseCache
from django.contrib.auth.models import User, Group, Permission
from django.test.client import Client
from django.utils import timezone

from . import forms, models, factories, typeahead, datasources
from talks.events.models import Event, EventGroup, Person, EVENT_IN_PREPARATION, EVENT_PUBLISHED
from talks.users.authentication import GROUP_EDIT_EVENTS

VALID_DATE_STRING = "2014-05-12 12:18"


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
        old_event.start = timezone.now() - datetime.timedelta(days=1);
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


class TestEventGroupForm(TestCase):

    def test_empty(self):
        form = forms.EventGroupForm({})
        self.assertEquals(form.is_valid(), False, "empty form should not validate")
        errors = form.errors.as_data()
        self.assertIn('title', errors)
        self.assertEquals(len(errors), 1)

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
        self.assertEquals(len(errors), 1)

    def test_all_fields_valid(self):
        data = {
            'description': u'something',
            'title': u'some title',
            'group_type': u'SE',
        }
        form = forms.EventGroupForm(data)
        self.assertEquals(form.is_valid(), True, "form should validate")


class AuthTestCase(TestCase):
    """Subclass AuthTestCase if you need to create/edit
    Event or EventGroup (requiring auth)
    """

    def setUp(self):
        self.client = Client()
        #Create the 'Contributors' group
        self.group = Group(name=GROUP_EDIT_EVENTS)
        self.group.save()

        #Add edit permissions for Event, EventGroup and Person
        content_types = ContentType.objects.get_for_models(Event, EventGroup, Person);
        permissions = Permission.objects.filter( content_type__in=content_types.values() )
        self.group.permissions.add(*permissions)
        self.group.save()

        username = 'test'
        password = 'test'
        self.user = User.objects.create_user(username, password=password)
        self.user.groups.add(self.group)
        self.user.save()
        self.client.login(username=username, password=password)


class TestEventGroupViews(AuthTestCase):

    def test_show_event_group_404(self):
        response = self.client.get("/talks/series/1")
        self.assertEquals(response.status_code, 404)

    def test_list_event_groups_empty(self):
        response = self.client.get("/talks/series/")
        self.assertEquals(response.status_code, 200)

    def test_list_event_groups_some(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/talks/series/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, group.title)

    def test_show_event_group_200(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/talks/series/id/%s" % group.slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, group.title)
        self.assertContains(response, group.description)

    def test_edit_event_group_404(self):
        response = self.client.get("/talks/series/id/1/edit")
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, "events/event_group_form.html")

    def test_edit_event_group_200(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get("/talks/series/id/%s/edit" % group.slug)
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

        response = self.client.post("/talks/series/id/%s/edit" % group.slug, data)
        self.assertRedirects(response, "/talks/series/id/%s" % group.slug)
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

        response = self.client.post("/talks/series/id/%s/edit" % group.slug, data)
        saved_group = models.EventGroup.objects.get(slug=group.slug)
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertEquals(saved_group.title, old_title)
        self.assertEquals(saved_group.description, old_description)
        self.assertTemplateUsed(response, "events/event_group_form.html")

    def test_create_event_group_200(self):
        response = self.client.get("/talks/series/new")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_group_form.html")

    def test_create_event_group_post_happy(self):
        data = {
            'title': 'lkfjlfkds',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/talks/series/new", data)
        saved_group = models.EventGroup.objects.get()
        self.assertRedirects(response, "/talks/series/id/%s" % saved_group.slug)
        self.assertEquals(saved_group.title, data['title'])
        self.assertEquals(saved_group.description, data['description'])
        self.assertTemplateNotUsed(response, "events/event_group_form.html")

    def test_create_event_group_post_invalid(self):
        data = {
            'title': '',
            'description': 'dflksfoingf',
            'group_type': '',
        }

        response = self.client.post("/talks/series/new", data)
        self.assertFormError(response, 'form', 'title', ['This field is required.'])
        self.assertQuerysetEqual(models.EventGroup.objects.all(), [])
        self.assertTemplateUsed(response, "events/event_group_form.html")


class TestCreateEventView(AuthTestCase):

    def test_get_happy_no_group_id(self):
        response = self.client.get('/talks/new')
        logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_form.html')
        self.assertContains(response, "Oxford Talks")
        self.assertContains(response, "Add Talk")
        self.assertIn('event_form', response.context)

    def test_get_nonexistent_group(self):
        response = self.client.get('/talks/series/8475623/new')
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, 'events/event_form.html')

    def test_get_happy_for_existing_group(self):
        group = factories.EventGroupFactory.create()
        response = self.client.get('/talks/series/%s/new' % group.slug)
        logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertEquals(response.status_code, 200)
        self.assertIn('event_form', response.context)
        self.assertEquals(response.context['event_form']['group'].value(), group.slug)

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

        response = self.client.post('/talks/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, '/talks/new')
        count = models.Event.objects.filter(title=title, description=description).count()
        self.assertEquals(count, 1, msg="Event instance was not saved")

    def test_post_valid_save_and_continue_with_group_id(self):
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        group = factories.EventGroupFactory.create()
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
            'event-group': group.slug,
            'name': u'',
            'event-booking_type': models.BOOKING_NOT_REQUIRED,
            'event-audience': models.AUDIENCE_PUBLIC,
            'event-status': models.EVENT_IN_PREPARATION,
        }

        response = self.client.post('/talks/series/%s/new' % group.slug, data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, '/talks/series/%s/new' % group.slug)
        count = models.Event.objects.filter(title=title, description=description, group__slug=group.slug).count()
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
        response = self.client.post('/talks/new', data)
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
        response = self.client.post('/talks/new', data)
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

        response = self.client.post('/talks/new', data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        try:
            event = models.Event.objects.get(title=title, description=description)
        except models.Event.DoesNotExist:
            self.fail("Event instance was not saved")
        logging.info("event.topics: %s", [t.uri for t in event.topics.all()])
        self.assertEquals({t.uri for t in topics}, {t.uri for t in event.topics.all()}, "topics were not assigned properly")
        self.assertRedirects(response, event.get_absolute_url())


class TestAuthorisation(TestCase):
    """
    Test that events can only be created and edited by users who should be allowed to do so
    """
    def setUp(self):
        """
        Creates users but doesn't log any of them in. The individual tests should do that
        """
        self.client = Client()
        #Create the 'Contributors' group
        self.group = Group(name=GROUP_EDIT_EVENTS)
        self.group.save()

        #Add edit permissions for Event, EventGroup and Person
        content_types = ContentType.objects.get_for_models(Event, EventGroup, Person);
        permissions = Permission.objects.filter( content_type__in=content_types.values() )
        self.group.permissions.add(*permissions)
        self.group.save()

        #user 1 who is member of contributors group
        self.username_contrib1 = 'c1'
        self.password_contrib1 = 'c1'
        self.contrib_user1 = User.objects.create_user(self.username_contrib1, password=self.password_contrib1)
        self.contrib_user1.groups.add(self.group)
        self.contrib_user1.save()

        #user 2 who is a member of contributors group
        self.username_contrib2 = 'c2'
        self.password_contrib2 = 'c2'
        self.contrib_user2 = User.objects.create_user(self.username_contrib2, password=self.password_contrib2)
        self.contrib_user2.groups.add(self.group)
        self.contrib_user2.save()

        #a non-contributing user
        self.username_non_contrib = "nc"
        self.password_non_contrib = "nc"
        self.nonContribUser = User.objects.create_user(self.username_non_contrib, password=self.password_non_contrib);
        self.nonContribUser.save()


    def test_edit_event_unauthorised(self):
        #create event and set user1 as an editor
        event = factories.EventFactory.create()
        event.editor_set.add(self.contrib_user2)
        event.save()

        #attempt to edit the event as contrib_user1
        self.client.login(username=self.username_contrib1, password=self.password_contrib1)
        data = {
            'event-title': 'lkfjlfkds'
        }
        response = self.client.post("/talks/id/%s/edit" % event.slug, data)
        self.assertEquals(response.status_code, 403)
        self.assertTemplateNotUsed(response, "events/event_form.html")

    def test_create_event_unauthorised(self):
        self.client.login(username=self.username_non_contrib, password=self.password_non_contrib)
        data = {
            'name' : u'',
            'event-start': VALID_DATE_STRING,
            'event-end' : VALID_DATE_STRING
        }
        response = self.client.post("/talks/new", data)
        self.assertEquals(response.status_code, 403)
        self.assertTemplateNotUsed(response, "events/event_form.html")


class TestEditEventView(AuthTestCase):

    def test_edit_event_404(self):
        response = self.client.get("/talks/id/1/edit")
        self.assertEquals(response.status_code, 404)
        self.assertTemplateNotUsed(response, "events/event_form.html")

    def test_edit_event_200(self):
        event = factories.EventFactory.create()
        event.editor_set.add(self.user)
        event.save()
        response = self.client.get("/talks/id/%s/edit" % event.slug)
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
        event.editor_set.add(self.user)
        event.save()
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

        response = self.client.post("/talks/id/%s/edit" % event.slug, data)
        if response.context:
            logging.info("Form errors: %s", response.context['event_form'].errors)
        self.assertRedirects(response, "/talks/id/%s/" % event.slug)
        saved_event = models.Event.objects.get(slug=event.slug)
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
        event.editor_set.add(self.user)
        event.save()
        data = {
            'event-title': '',
            'event-description': 'dflksfoingf',
        }

        response = self.client.post("/talks/id/%s/edit" % event.slug, data)
        saved_event = models.Event.objects.get(slug=event.slug)
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
