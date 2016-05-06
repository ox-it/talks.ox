# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_remove_event_speaker_tba'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='audience',
            field=models.TextField(default=b'oxonly', verbose_name=b'Who can attend'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.TextField(default=b'published', verbose_name=b'Status', choices=[(b'preparation', b'In preparation'), (b'published', b'Published'), (b'cancelled', b'Cancelled')]),
            preserve_default=True,
        ),
    ]
