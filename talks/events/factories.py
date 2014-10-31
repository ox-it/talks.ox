import factory

from . import models


class EventGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventGroup


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Person


class TopicItemFactory(factory.django.DjangoModelFactory):
    item = factory.SubFactory(EventFactory)

    @factory.sequence
    def uri(n):
        return "http://example.com/%s" % n

    class Meta:
        model = models.TopicItem
