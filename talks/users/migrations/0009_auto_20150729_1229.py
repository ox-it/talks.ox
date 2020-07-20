# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations

import uuid

def save_each_collection(apps, schema_editor):
    # Save each collection to generate slugs.
    Collection = apps.get_model('users.collection')
    for collection in Collection.objects.all():
        if not collection.slug:
            collection.slug = str(uuid.uuid4())
        collection.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_talksusercollection_is_main'),
    ]

    operations = [
        migrations.RunPython(save_each_collection)
    ]
