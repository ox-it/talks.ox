# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldTalk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_talk_id', models.CharField(max_length=20)),
                ('event', models.ForeignKey(to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OldSeries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_series_id', models.CharField(max_length=20)),
                ('group', models.ForeignKey(to='events.EventGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
