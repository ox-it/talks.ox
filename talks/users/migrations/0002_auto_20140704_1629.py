# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='collectionfollow',
            unique_together=set([(b'user', b'collection'), (b'user', b'is_main')]),
        ),
    ]
