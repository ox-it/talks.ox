from __future__ import absolute_import
from django.test import TestCase

from .utils import compare_dicts, IGNORE_FIELDS


class CompareDictsTest(TestCase):

    def test_dict_none(self):
        """Ensure "old" dict get expected result
        """
        new = {'a': 'b', 'c': 'd'}
        result = compare_dicts(new, None)
        for k in new.keys():
            self.assertEqual(result[k], (new[k], None, False))

    def test_ignored_keys(self):
        """Ensure ignored keys are not in the result
        """
        new = {'a': 'b', 'c': 'd'}
        old = {'a': 'b', 'c': 'd'}
        for field in IGNORE_FIELDS:
            new[field] = field
            old[field] = field
        result = compare_dicts(new, old)
        for field in IGNORE_FIELDS:
            self.assertNotIn(field, result)

    def test_same_dicts(self):
        """Ensure ignored keys are not in the result
        """
        new = {'a': 'b', 'c': 'd'}
        old = {'a': 'b', 'c': 'd'}
        result = compare_dicts(new, old)
        for k, v in result.items():
            self.assertEqual(v, (new[k], old[k], False))

    def test_different_keys(self):
        """Test with two dict
        """
        new = {'albumin': 12, 'fbc': 'yes', 'phosphate': True}
        old = {'albumin': 15, 'fbc': 'yes', 'phosphate': False}
        result = compare_dicts(new, old)
        for k, v in result.items():
            self.assertEqual(v, (new[k], old[k], new[k] != old[k]))
