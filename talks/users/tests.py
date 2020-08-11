from __future__ import absolute_import
from django.test import TestCase
from django.contrib.auth.models import User, Group

from .authentication import GROUP_EDIT_EVENTS, user_in_group_or_super


class TestAuthorisation(TestCase):

    def test_authorisation_expression(self):
        normal_user = User.objects.create_user('normal', 'normal@uni.ox', 'password')
        super_user = User.objects.create_superuser('super', 'super@uni.ox', 'password')
        contrib_group = Group()
        contrib_group.name = GROUP_EDIT_EVENTS
        contrib_group.save()
        contributor_user = User.objects.create_user('contributor', 'contributor@uni.ox', 'password')
        contributor_user.groups.add(contrib_group)
        contributor_user.save()

        self.assertTrue(user_in_group_or_super(super_user))
        self.assertTrue(user_in_group_or_super(contributor_user))
        self.assertFalse(user_in_group_or_super(normal_user))
