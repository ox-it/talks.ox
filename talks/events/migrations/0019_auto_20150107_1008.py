# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_event_organiser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventgroup',
            name='organiser',
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='organisers',
            field=models.ManyToManyField(to='events.Person', null=True, blank=True),
            preserve_default=True,
        ),
    ]
