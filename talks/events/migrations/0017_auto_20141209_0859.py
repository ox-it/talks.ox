# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20141208_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='booking_email',
            field=models.EmailField(default=b'', max_length=75, verbose_name=b'Email address for booking', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='audience',
            field=models.TextField(default=b'oxonly', verbose_name=b'Who can attend', choices=[(b'oxonly', b'Members of the University only'), (b'public', b'Public')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.TextField(default=b'preparation', verbose_name=b'Status', choices=[(b'preparation', b'In preparation'), (b'published', b'Published')]),
            preserve_default=True,
        ),
    ]
