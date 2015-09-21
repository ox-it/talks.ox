# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20150729_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='editor_set',
            field=models.ManyToManyField(to='users.TalksUser', through='users.TalksUserCollection', blank=True),
            preserve_default=True,
        ),
    ]
