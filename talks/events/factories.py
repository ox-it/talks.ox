import factory

from . import models


class EventGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventGroup


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event
