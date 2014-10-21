import unittest

from django.test import TestCase

from . import forms


class TestEventForm(TestCase):

    def test_empty(self):
        form = forms.EventForm({})
        self.assertEquals(form.is_valid(), False, "empty form should not validate")
        errors = form.errors.as_data()
        self.assertEquals(len(errors), 2)
        self.assertIn('title', errors)
        self.assertIn('description', errors)

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
        self.assertEquals(len(errors), 2)
        self.assertIn('title', errors)
        self.assertIn('description', errors)

    def test_invalid_date(self):
        data = {
            'description': u'',
            'title': u'',
            'location': u'',
            'department_suggest': u'',
            'start': u'94872394',
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
        self.assertEquals(len(errors), 3)
        self.assertIn('title', errors)
        self.assertIn('description', errors)
        self.assertIn('start', errors)


class TestEventGroupForm(TestCase):

    def test_empty(self):
        form = forms.EventGroupForm({})
        self.assertEquals(form.is_valid(), True, "empty form should validate")

    @unittest.skip("not actually true")
    def test_enabled(self):
        form = forms.EventGroupForm({
            'enabled': False,
            'foo': 'fldsjhfdsff',
            'title': 32434,
            'event_group_select': 'this is not a valid pk of event group',
            'select_create': 'definitely invalid choice'
        })
        self.assertEquals(form.is_valid(), {}, "if enabled is set the form should accept anything")

    def test_all_fields_blanked(self):
        return
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
        form = forms.EventGroupForm(data)
        self.assertEquals(form.is_valid(), False, "blanked form should not validate")
        errors = form.errors.as_data()
        self.assertEquals(len(errors), 2)
        self.assertIn('title', errors)
        self.assertIn('description', errors)

