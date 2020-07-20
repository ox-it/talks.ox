# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_collecteddepartment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='talksusercollection',
            options={'verbose_name': 'Public Collection Ownership', 'verbose_name_plural': 'Public Collection Ownerships'},
        ),
    ]
