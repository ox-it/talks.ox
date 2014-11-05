import unittest
import logging

from django.test import TestCase

from . import forms, models, factories

VALID_DATE_STRING = "2014-05-12 12:18"


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
            'event-department_suggest': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': u'',
            'event-speaker_suggest': u'',
            'event-group-description': u'',
            'event-location_suggest': u'',
            'event-department_organiser': u'',
            'event-group-event_group_select': u'',
            'event-speakers': u'',
            'event-group-group_type': u'',
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-group-select_create': u'CRE',
            'event-topic_suggest': u'',
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
            'event-department_suggest': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': u'',
            'event-speaker_suggest': u'',
            'event-location_suggest': u'',
            'event-department_organiser': u'',
            'event-speakers': u'',
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

    def test_post_valid(self):
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        data = {
            'event-description': description,
            'event-title': title,
            'event-group': u'',
            'event-location': u'',
            'event-department_suggest': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': u'',
            'event-speaker_suggest': u'',
            'event-location_suggest': u'',
            'event-department_organiser': u'',
            'event-speakers': u'',
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-topic_suggest': u'',
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

    def test_post_valid_with_speakers(self):
        title = u'cjwnf887y98fw'
        description = u'kfjdnsf'
        speakers = factories.PersonFactory.create_batch(3)
        data = {
            'event-description': description,
            'event-title': title,
            'event-group': u'',
            'event-location': u'',
            'event-department_suggest': u'',
            'email_address': u'',
            'event-start': VALID_DATE_STRING,
            'event-topics': u'',
            'event-speaker_suggest': u'some junk',
            'event-location_suggest': u'',
            'event-department_organiser': u'',
            'event-speakers': u','.join([str(s.pk) for s in speakers]),
            'csrfmiddlewaretoken': u'3kHyJXv0HDO8sJPLlpvQhnBqM04cIJAM',
            'event-topic_suggest': u'',
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

    def test_edit_event_post_happy(self):
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

    def test_get_no_embargo(self):
        events = models.Event.objects.all()
        self.assertEqual(len(events), 2)
        self.assertEqual(set(events), set([self.draft, self.published]))

    def test_published(self):
        events = models.Event.objects.published()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], self.published)