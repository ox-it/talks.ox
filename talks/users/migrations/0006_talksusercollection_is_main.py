# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150728_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='talksusercollection',
            name='is_main',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
