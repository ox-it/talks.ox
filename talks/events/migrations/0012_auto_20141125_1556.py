# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.TextField(default=b'preparation', verbose_name=b'Status', choices=[(b'published', b'Published'), (b'preparation', b'In preparation')]),
            preserve_default=True,
        ),
    ]
