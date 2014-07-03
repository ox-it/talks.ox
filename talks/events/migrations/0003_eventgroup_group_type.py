# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_speaker_email_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventgroup',
            name='group_type',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'SE', b'Seminar Series'), (b'CO', b'Conference')]),
            preserve_default=True,
        ),
    ]
