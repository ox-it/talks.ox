# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20141028_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location_details',
            field=models.TextField(default=b'', help_text=b'e.g.: room number or accessibility information', verbose_name=b'Additional details', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='booking_type',
            field=models.TextField(default=b'nr', verbose_name=b'Booking required', choices=[(b'nr', b'Not required'), (b're', b'Required'), (b'rc', b'Recommended')]),
        ),
    ]
