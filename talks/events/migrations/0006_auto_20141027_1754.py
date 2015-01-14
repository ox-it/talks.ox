# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20140716_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(related_name=b'events', blank=True, to='events.EventGroup', null=True),
        ),
    ]
