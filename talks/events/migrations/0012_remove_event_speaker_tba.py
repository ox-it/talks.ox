# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_auto_20160425_1731'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='speaker_tba',
        ),
    ]
