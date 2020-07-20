# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_eventgroup_editor_set'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
