# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_event_editor_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventgroup',
            name='department',
            field=models.TextField(default=b'', blank=True),
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
            name='organiser',
            field=models.ForeignKey(blank=True, to='events.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='web_address',
            field=models.URLField(default=b'', verbose_name=b'Web address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='editor_set',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personevent',
            name='role',
            field=models.TextField(default=b'speaker', choices=[(b'speaker', b'Speaker'), (b'host', b'Host'), (b'organiser', b'Organiser')]),
            preserve_default=True,
        ),
    ]
