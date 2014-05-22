from django.db import models


class Series(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()


class Speaker(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()


class Location(models.Model):
    oxpoints_id = models.CharField(db_index=True,
                                   unique=True,
                                   max_length=50)
    name = models.CharField(max_length=250)
    # TODO what should be stored here? what IS a location?
    # (e.g. building vs actual room of the event)
    # (e.g. additional information, accessibility etc)


class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    # TODO audience should it be free text
    # TODO booking information; structure?

    series = models.ForeignKey(Series, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)


class Talk(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    # TODO audience should it be free text
    # TODO booking information; structure?

    event = models.ForeignKey(Event)
    speaker = models.ManyToManyField(Speaker, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
