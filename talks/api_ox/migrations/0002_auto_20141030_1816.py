# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '__first__'),
        ('api_ox', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.DeleteModel(
            name='Organisation',
        ),
    ]
