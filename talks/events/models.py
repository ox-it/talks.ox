import logging
import functools

from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import date as date_filter
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from talks.api_ox.api import ApiException, OxfordDateResource, PlacesResource, TopicsResource
from talks.api_ox.models import Location, Organisation


logger = logging.getLogger(__name__)


class EventGroupManager(models.Manager):
    def for_events(self, events):
        """Given a QuerySet of `Event`s return all the `EventGroup` related to
        that QuerySet. This function will evaluate the QuerySet `events`.

        Returns a list() of `EventGroup` NOT a QuerySet.
        """
        events = events.select_related('group')
        # NOTE: execs the query
        return set([e.group for e in events if e.group])


class EventGroup(models.Model):
    SEMINAR = 'SE'
    CONFERENCE = 'CO'
    EVENT_GROUP_TYPE_CHOICES = (
        (SEMINAR, 'Seminar Series'),
        (CONFERENCE, 'Conference'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    group_type = models.CharField(
        blank=True,
        null=True,
        max_length=2,
        choices=EVENT_GROUP_TYPE_CHOICES
    )

    objects = EventGroupManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event-group', args=[self.id])

class SpeakerManager(models.Manager):

    def suggestions(self, query):
        return self.filter(name__icontains=query)


class Speaker(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()
    email_address = models.EmailField(max_length=254)

    objects = SpeakerManager()

    def __unicode__(self):
        return self.name


class Topic(models.Model):

    name = models.CharField(max_length=250)
    uri = models.URLField(unique=True, db_index=True)

    def __unicode__(self):
        return self.name


class TopicItem(models.Model):

    topic = models.ForeignKey(Topic)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')   # atm: Event, EventGroup


class EventManager(models.Manager):

    def todays_events(self):
        return self.future_events(timedelta(days=1))

    def future_events(self, td):
        """Fetch future events from today for the next X delta
        :param td: timedelta object
        :return: QuerySet
        """
        today = date.today()
        to = today + td
        return self.filter(start__gte=today, start__lt=to).order_by('start')


class Event(models.Model):
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    speakers = models.ManyToManyField(Speaker, null=True, blank=True)
    # TODO audience should it be free text
    # TODO booking information; structure?

    group = models.ForeignKey(EventGroup, null=True, blank=True,
                              related_name='events')
    location = models.ForeignKey(Location, null=True, blank=True)
    # TODO I'm guessing an event can be organised by multiple departments?
    department_organiser = models.ForeignKey(Organisation, null=True, blank=True)

    topics = GenericRelation(TopicItem)

    objects = EventManager()

    _cached_resources = {}

    def fetch_resource(self, key, func):
        """Fetch a resource from the API.

        If we have `key` in a cache then pull from there, otherwise call `func`
        """
        if key in self._cached_resources:
            return self._cached_resources[key]
        else:
            try:
                res = func()
                self._cached_resources[key] = res
                return res
            except ApiException:
                logger.warn('Unable to reach API', exc_info=True)
                return None

    @property
    def api_location(self):
        if not self.location:
            return None
        func = functools.partial(PlacesResource.from_identifier,
                                 self.location.identifier)
        return self.fetch_resource(self.location.identifier, func)

    @property
    def api_organisation(self):
        if not self.department_organiser:
            return None
        func = functools.partial(PlacesResource.from_identifier,
                                 self.department_organiser.identifier)
        return self.fetch_resource(self.department_organiser.identifier, func)

    @property
    def oxford_date(self):
        if not self.start:
            return None
        func = functools.partial(OxfordDateResource.from_date, self.start)
        return self.fetch_resource(self.start, func)

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

    def formatted_date(self):
        if self.start:
            return date_filter(self.start, settings.EVENT_DATETIME_FORMAT)
        else:
            return None

    def formatted_time(self):
        if self.start:
            return date_filter(self.start, settings.EVENT_TIME_FORMAT)
        else:
            return None

    def happening_today(self):
        if self.start:
            return self.start.date() == date.today()
        return False


@receiver(models.signals.post_save, sender=Event)
def index_event(sender, instance, created, **kwargs):
    """If the User has just been created we use a signal to also create a TalksUser
    """
    pass


@receiver(models.signals.post_save, sender=Event)
def fetch_topics(sender, instance, created, **kwargs):
    """If the User has just been created we use a signal to also create a TalksUser
    """
    return      # TODO to be discussed
    uris = [topic.uri for topic in instance.topics.all()]
    cached_topics = Topic.objects.filter(uri__in=uris)
    cached_topics_uris = [topic.uri for topic in cached_topics]
    missing_topics_uris = set(uris) - set(cached_topics_uris)
    logger.info("Fetching missing topics {uris}".format(uris=missing_topics_uris))
    topics = TopicsResource.get(missing_topics_uris)
    for topic in topics:
        Topic.objects.create(name=topic.name, uri=topic.uri)


@receiver(models.signals.post_save, sender=Topic)
def fetch_topic(sender, instance, created, **kwargs):
    """Populate the topic name if it is empty by fetching
    it from the API.
    """
    if created and not instance.name:
        topic = TopicsResource.get([instance.uri])
        topic = topic[0]
        instance.name = topic.name
        instance.save()
