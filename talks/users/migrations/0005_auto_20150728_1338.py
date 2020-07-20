# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_collection_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='TalksUserCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.TextField(default=b'owner', choices=[(b'owner', b'Owner'), (b'editor', b'Collaborator'), (b'reader', b'Viewer')])),
                ('collection', models.ForeignKey(to='users.Collection', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to='users.TalksUser', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='collectionfollow',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='collectionfollow',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='collectionfollow',
            name='user',
        ),
        migrations.DeleteModel(
            name='CollectionFollow',
        ),
        migrations.AddField(
            model_name='talksuser',
            name='collections',
            field=models.ManyToManyField(to='users.Collection', through='users.TalksUserCollection', blank=True),
            preserve_default=True,
        ),
    ]
