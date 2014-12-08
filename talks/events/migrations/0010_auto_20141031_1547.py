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
            name='embargo',
            field=models.BooleanField(default=False, verbose_name=b'Embargo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.TextField(default=b'PREP', verbose_name=b'Status', choices=[(b'PUB', b'Published'), (b'PREP', b'In preparation')]),
            preserve_default=True,
        ),
    ]
