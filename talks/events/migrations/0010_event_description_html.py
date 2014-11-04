# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20141030_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description_html',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
