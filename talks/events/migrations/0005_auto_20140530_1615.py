# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20140528_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(to_field='id', blank=True, to='events.EventGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(to='events.Speaker', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='event',
            name='series',
        ),
        migrations.DeleteModel(
            name='Talk',
        ),
        migrations.DeleteModel(
            name='Series',
        ),
    ]
