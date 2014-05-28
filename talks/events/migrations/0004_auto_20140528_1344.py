# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        ('events', '0003_auto_20140521_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name', models.CharField(unique=True, max_length=250)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(to='events.Tag', to_field='id')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', to_field='id')),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='talk',
            name='department_organiser',
            field=models.ForeignKey(to_field='id', blank=True, to='api_ox.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='department_organiser',
            field=models.ForeignKey(to_field='id', blank=True, to='api_ox.Organisation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='speaker',
            field=models.ManyToManyField(to='events.Speaker', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='location',
            field=models.ForeignKey(to_field='id', blank=True, to='api_ox.Location', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.ForeignKey(to_field='id', blank=True, to='api_ox.Location', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='series',
            field=models.ForeignKey(to_field='id', blank=True, to='events.Series', null=True),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
