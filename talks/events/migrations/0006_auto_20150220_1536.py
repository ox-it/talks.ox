# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def extract_lastname(apps, schema_editor):
    # Extract the last name of each person in the database
    Person = apps.get_model('events', "Person")
    for person in Person.objects.all():
        person.lastname = person.name.split(' ')[-1]
        person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_person_lastname'),
    ]

    operations = [
        migrations.RunPython(extract_lastname)
    ]
