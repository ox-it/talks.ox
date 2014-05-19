# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='series',
            field=models.ForeignKey(to='events.Series', to_field='id', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='event',
            field=models.ForeignKey(to='events.Event', default=1, to_field='id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='talk',
            name='speaker',
            field=models.ManyToManyField(to='events.Speaker', null=True),
            preserve_default=True,
        ),
    ]
