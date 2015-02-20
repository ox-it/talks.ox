# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20150219_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='lastname',
            field=models.CharField(default='z', max_length=250),
            preserve_default=False,
        ),
    ]
