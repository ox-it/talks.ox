# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20141128_1531'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventgroup',
            old_name='department',
            new_name='department_organiser',
        ),
    ]
