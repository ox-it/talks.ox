# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20141201_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='location_details',
            field=models.TextField(default=b'', help_text=b'e.g.: room number or accessibility information', verbose_name=b'Venue details', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='special_message',
            field=models.TextField(default=b'', help_text=b'Use this for important notices - e.g.: cancellation or a last minute change of venue', verbose_name=b'Special message', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='department_organiser',
            field=models.TextField(default=b'', verbose_name=b'Organising Department', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='group_type',
            field=models.CharField(default=b'SE', max_length=2, null=True, blank=True, choices=[(b'SE', b'Seminar Series'), (b'CO', b'Conference')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='bio',
            field=models.TextField(verbose_name=b'Affiliation'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='email_address',
            field=models.EmailField(max_length=254, null=True, blank=True),
            preserve_default=True,
        ),
    ]
