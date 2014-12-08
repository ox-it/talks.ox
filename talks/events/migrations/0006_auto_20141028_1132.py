# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


MIGRATE_SPEAKERS_SQL_FORWARD = """INSERT INTO events_personevent (event_id, person_id, affiliation, role, url) SELECT event_id, person_id, '', 'speaker', '' FROM events_event_speakers;"""

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20140716_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('affiliation', models.TextField(blank=True)),
                ('role', models.TextField(default=b'speaker', choices=[(b'speaker', b'Speaker'), (b'host', b'Host'), (b'organizer', b'Organizer')])),
                ('url', models.URLField(blank=True)),
                ('event', models.ForeignKey(to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='Speaker',
            new_name='Person',
        ),
        migrations.AddField(
            model_name='personevent',
            name='person',
            field=models.ForeignKey(to='events.Person'),
            preserve_default=True,
        ),
        migrations.RunSQL(MIGRATE_SPEAKERS_SQL_FORWARD),
        migrations.RemoveField(
            model_name='event',
            name='speakers',
        ),
        migrations.AddField(
            model_name='event',
            name='person_set',
            field=models.ManyToManyField(to='events.Person', through='events.PersonEvent', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(related_name=b'events', blank=True, to='events.EventGroup', null=True),
        ),
    ]
