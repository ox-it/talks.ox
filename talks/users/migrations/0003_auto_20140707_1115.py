# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20140704_1629'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='collectionitem',
            unique_together=set([(b'collection', b'content_type', b'object_id')]),
        ),
    ]
