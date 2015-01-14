# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_squashed_0009_merge'),
        ('old_talks', '0001_initial'),
    ]

    operations = [
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
