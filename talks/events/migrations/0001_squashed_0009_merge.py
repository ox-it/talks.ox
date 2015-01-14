# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        ('api_ox', '__first__'),
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
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField()),
                ('bio', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('title', models.CharField(max_length=250)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('group', models.ForeignKey(to_field='id', blank=True, to='events.EventGroup', null=True)),
                ('location', models.ForeignKey(to_field='id', blank=True, to='api_ox.Location', null=True)),
                ('department_organiser', models.ForeignKey(to_field='id', blank=True, to='api_ox.Organisation', null=True)),
                ('speakers', models.ManyToManyField(to=b'events.Speaker', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='speaker',
            name='email_address',
            field=models.EmailField(default='example@example.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='group_type',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'SE', b'Seminar Series'), (b'CO', b'Conference')]),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250)),
                ('uri', models.URLField(unique=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('topic', models.ForeignKey(to='events.Topic')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(max_length=250),
        ),
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
        migrations.RunSQL(
            sql="INSERT INTO events_personevent (event_id, person_id, affiliation, role, url) SELECT event_id, person_id, '', 'speaker', '' FROM events_event_speakers;",
            reverse_sql=None,
            state_operations=None,
        ),
        migrations.RemoveField(
            model_name='event',
            name='speakers',
        ),
        migrations.AddField(
            model_name='event',
            name='person_set',
            field=models.ManyToManyField(to=b'events.Person', through='events.PersonEvent', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(related_name=b'events', blank=True, to='events.EventGroup', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='audience',
            field=models.TextField(default=b'oxonly', verbose_name=b'Who can attend', choices=[(b'public', b'Public'), (b'oxonly', b'Members of the University only')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='booking_type',
            field=models.TextField(default=b'nr', verbose_name=b'Booking required', choices=[(b'nr', b'Not required'), (b're', b'Required'), (b'rc', b'Recommended')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='booking_url',
            field=models.URLField(default=b'', verbose_name=b'Web address for booking', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='cost',
            field=models.TextField(default=b'', help_text=b'If applicable', verbose_name=b'Cost', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='special_message',
            field=models.TextField(default=b'', help_text=b'Use this for important notices - e.g.: cancellation or a last minute change of venue.', verbose_name=b'Special message', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='title_not_announced',
            field=models.BooleanField(default=False, verbose_name=b'Title to be announced'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='location_details',
            field=models.TextField(default=b'', help_text=b'e.g.: room number or accessibility information', verbose_name=b'Additional details', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(related_name=b'events', blank=True, to='events.EventGroup', null=True),
        ),
    ]
