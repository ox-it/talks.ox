# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField()),
                ('bio', models.TextField()),
                ('email_address', models.EmailField(max_length=254, null=True, blank=True))
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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='group_type',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'SE', b'Seminar Series'), (b'CO', b'Conference')]),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='TopicItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
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
        migrations.AddField(
            model_name='personevent',
            name='person',
            field=models.ForeignKey(to='events.Person'),
            preserve_default=True,
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
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='audience',
            field=models.TextField(default=b'oxonly', verbose_name=b'Who can attend', choices=[(b'oxonly', b'Members of the University only'), (b'public', b'Public')]),
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
            field=models.TextField(default=b'', help_text=b'Use this for important notices - e.g.: cancellation or a last minute change of venue', verbose_name=b'Special message', blank=True),
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
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='location_details',
            field=models.TextField(default=b'', help_text=b'e.g.: room number or accessibility information', verbose_name=b'Venue details', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.ForeignKey(related_name=b'events', blank=True, to='events.EventGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicitem',
            name='uri',
            field=models.URLField(default='', db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='department_organiser',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='topicitem',
            unique_together=set([('uri', 'content_type', 'object_id')]),
        ),
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='embargo',
            field=models.BooleanField(default=False, verbose_name=b'Embargo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.TextField(default=b'preparation', verbose_name=b'Status', choices=[(b'preparation', b'In preparation'), (b'published', b'Published')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='editor_set',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='department_organiser',
            field=models.TextField(default=b'', verbose_name=b'Organising Department', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='occurence',
            field=models.TextField(default=b'', help_text=b'e.g.: Mondays at 10 or September 19th to 20th.', verbose_name=b'Timing', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='web_address',
            field=models.URLField(default=b'', verbose_name=b'Web address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personevent',
            name='role',
            field=models.TextField(default=b'speaker', choices=[(b'speaker', b'Speaker'), (b'host', b'Host'), (b'organiser', b'Organiser')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='group_type',
            field=models.CharField(default=b'SE', max_length=2, null=True, blank=True, choices=[(b'SE', b'Seminar Series'), (b'CO', b'Conference')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='bio',
            field=models.TextField(verbose_name=b'Affiliation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='booking_email',
            field=models.EmailField(default=b'', max_length=75, verbose_name=b'Email address for booking', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='organiser_email',
            field=models.EmailField(default=b'', max_length=75, verbose_name=b'Organiser contact email', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='organisers',
            field=models.ManyToManyField(to=b'events.Person', null=True, blank=True),
            preserve_default=True,
        ),
    ]
