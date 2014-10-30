# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_ox', '0001_initial'),
        ('events', '0008_auto_20141029_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventgroup',
            name='department',
            field=models.ForeignKey(blank=True, to='api_ox.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='occurence',
            field=models.TextField(default=b'', help_text=b'e.g.: Mondays at 10 or September 19th to 20th.', verbose_name=b'Timing', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='organizer',
            field=models.ForeignKey(blank=True, to='events.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='web_address',
            field=models.URLField(default=b'', verbose_name=b'Web address', blank=True),
            preserve_default=True,
        ),
    ]
