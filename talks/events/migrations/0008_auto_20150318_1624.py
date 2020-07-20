# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20150225_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='bio',
            field=models.TextField(null=True, verbose_name=b'Affiliation', blank=True),
            preserve_default=True,
        ),
    ]
