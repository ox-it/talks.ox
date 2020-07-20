# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20150220_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='lastname',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
