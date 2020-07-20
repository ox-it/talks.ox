# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20160425_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='speaker_tba',
            field=models.BooleanField(default=True, verbose_name=b'Speaker to be announced'),
            preserve_default=True,
        ),
    ]
