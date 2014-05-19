from django.db import models


class Series(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()


class Speaker(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()


class Event(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()

    series = models.ForeignKey(Series, null=True)


class Talk(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()

    event = models.ForeignKey(Event)
    speaker = models.ManyToManyField(Speaker, null=True)
