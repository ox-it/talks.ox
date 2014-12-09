# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20141209_0859'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='organiser_email',
            field=models.EmailField(default=b'', max_length=75, verbose_name=b'Organiser contact email', blank=True),
            preserve_default=True,
        ),
    ]
