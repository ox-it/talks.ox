from datetime import datetime

import factory

from . import models
from talks.users.models import Collection, CollectionItem, CollectedDepartment


class EventGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventGroup

class EventCollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection


class EventFactory(factory.django.DjangoModelFactory):
    start = datetime(2015, 10, 23, 12, 18)
    end = datetime(2015, 10, 30, 20, 25)

    class Meta:
        model = models.Event


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Person


class PersonEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PersonEvent


class TopicItemFactory(factory.django.DjangoModelFactory):
    item = factory.SubFactory(EventFactory)

    @factory.sequence
    def uri(n):
        return "http://example.com/%s" % n

    class Meta:
        model = models.TopicItem


class TopicItemFactory_noSubFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TopicItem

class CollectedDepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollectedDepartment
        
class CollectionItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollectionItem
