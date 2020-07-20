# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
import pytz
import django.utils.timezone
from django.db import models, migrations


def utc_timezone_adjust(apps, schema_editor):
    # If event time is in BST then delete an hour from it to make it UTC.
    Event = apps.get_model('events', "Event")
    for event in Event.objects.all():
        # lose existing (incorrect) timezone info
        start = django.utils.timezone.make_naive(event.start, pytz.utc)
        end = django.utils.timezone.make_naive(event.end, pytz.utc)

        # make correct time
        event.start = pytz.timezone("Europe/London").localize(start)
        event.end = pytz.timezone("Europe/London").localize(end)

        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20150318_1624'),
    ]

    operations = [
        migrations.RunPython(utc_timezone_adjust)
    ]
