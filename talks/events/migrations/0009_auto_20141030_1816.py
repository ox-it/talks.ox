# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_squashed_0009_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topicitem',
            name='topic',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
        migrations.AddField(
            model_name='topicitem',
            name='uri',
            field=models.URLField(default='', db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='department_organiser',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.TextField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='topicitem',
            unique_together=set([('uri', 'content_type', 'object_id')]),
        ),
    ]
