# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='email_address',
            field=models.EmailField(default='example@example.com', max_length=254),
            preserve_default=False,
        ),
    ]
