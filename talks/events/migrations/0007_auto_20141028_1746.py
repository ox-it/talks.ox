# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20141028_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='audience',
            field=models.TextField(default=b'oxonly', verbose_name=b'Who can attend', choices=[(b'public', b'Public'), (b'oxonly', b'Members of the University only')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='booking_type',
            field=models.TextField(default=b'nr', verbose_name=b'Booking required', choices=[(b'nr', b'not required'), (b're', b'required'), (b'rc', b'recommended')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='booking_url',
            field=models.URLField(default=b'', verbose_name=b'Web address for booking', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='cost',
            field=models.TextField(default=b'', help_text=b'If applicable', verbose_name=b'Cost', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='special_message',
            field=models.TextField(default=b'', help_text=b'Use this for important notices - e.g.: cancellation or a last minute change of venue.', verbose_name=b'Special message', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='title_not_announced',
            field=models.BooleanField(default=False, verbose_name=b'Title to be announced'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=250, blank=True),
        ),
    ]
