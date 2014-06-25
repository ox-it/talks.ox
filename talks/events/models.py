from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from talks.api_ox.models import Location, Organisation


class EventGroup(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()

    def __unicode__(self):
        return self.title


class Speaker(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()

    def to_dict(self):
        result = {}
        if self.id:
            result['id'] = self.id
        if self.name:
            result['name'] = self.name
        if self.slug:
            result['slug'] = self.slug
        if self.bio:
            result['bio'] = self.bio
        return result


    def __unicode__(self):
        return self.name


class Tag(models.Model):

    slug = models.SlugField()
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class TagItem(models.Model):

    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')   # atm: Event, EventGroup


class Event(models.Model):
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    speakers = models.ManyToManyField(Speaker, null=True, blank=True)
    # TODO audience should it be free text
    # TODO booking information; structure?

    group = models.ForeignKey(EventGroup, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    # TODO I'm guessing an event can be organised by multiple departments?
    department_organiser = models.ForeignKey(Organisation, null=True, blank=True)

    tags = GenericRelation(TagItem)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.title)
        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Event: {title} ({start})".format(title=self.title,
                                          start=self.start.strftime("%Y-%m-%d %H:%M"))

    def get_absolute_url(self):
        return reverse('event', args=[str(self.id)])
