# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_utc_timezone_adjust'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='speaker_tba',
            field=models.BooleanField(default=False, verbose_name=b'Speaker to be announced'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='various_speakers',
            field=models.BooleanField(default=False, verbose_name=b'Various Speakers'),
            preserve_default=True,
        ),
    ]
