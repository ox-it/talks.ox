# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_squashed_0019_auto_20150107_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='web_address',
            field=models.URLField(null=True, verbose_name=b'Web address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='organiser_email',
            field=models.EmailField(default=b'', max_length=75, verbose_name=b'Contact email', blank=True),
            preserve_default=True,
        ),
    ]
