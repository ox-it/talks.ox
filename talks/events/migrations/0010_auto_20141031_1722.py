# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20141030_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateTimeField(),
        ),
    ]
