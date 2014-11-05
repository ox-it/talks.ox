import logging
import functools
from datetime import date, timedelta

import reversion

from django.conf import settings
from django.db import models
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import date as date_filter
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from haystack.forms import model_choices

from talks.api_ox.api import ApiException, OxfordDateResource, PlacesResource, TopicsResource


logger = logging.getLogger(__name__)

ROLES_SPEAKER = 'speaker'
ROLES_HOST = 'host'
ROLES_ORGANIZER = 'organizer'
ROLES = (
    (ROLES_SPEAKER, 'Speaker'),
    (ROLES_HOST, 'Host'),
    (ROLES_ORGANIZER, 'Organizer'),
)

BOOKING_NOT_REQUIRED = 'nr'
BOOKING_REQUIRED = 're'
BOOKIND_RECOMMENDED = 'rc'

BOOKING_CHOICES = (
    (BOOKING_NOT_REQUIRED, 'Not required'),
    (BOOKING_REQUIRED, 'Required'),
    (BOOKIND_RECOMMENDED, 'Recommended'),
)

AUDIENCE_PUBLIC = 'public'
AUDIENCE_OXFORD = 'oxonly'
AUDIENCE_CHOICES = (
    (AUDIENCE_PUBLIC, 'Public'),
    (AUDIENCE_OXFORD, 'Members of the University only'),
)

EVENT_PUBLISHED = 'PUB'
EVENT_IN_PREPARATION = 'PREP'
EVENT_STATUS_CHOICES = (
    (EVENT_PUBLISHED, 'Published'),
    (EVENT_IN_PREPARATION, 'In preparation'),
)


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
        return reverse('show-event-group', args=[self.id])


class PersonManager(models.Manager):

    def suggestions(self, query):
        return self.filter(name__icontains=query)


class Person(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()
    email_address = models.EmailField(max_length=254)

    objects = PersonManager()

    def __unicode__(self):
        return self.name


class TopicItem(models.Model):

    uri = models.URLField(db_index=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')   # atm: Event, EventGroup

    class Meta:
        unique_together = ('uri', 'content_type', 'object_id')


class PersonEvent(models.Model):
    person = models.ForeignKey(Person)
    event = models.ForeignKey("Event")
    affiliation = models.TextField(blank=True)
    role = models.TextField(choices=ROLES, default=ROLES_SPEAKER)
    url = models.URLField(blank=True)


class EventQuerySet(models.QuerySet):

    def published(self):
        return self.filter(status=EVENT_PUBLISHED)


class EventManager(models.Manager):

    def get_query_set(self):
        return EventQuerySet(self.model).filter(embargo=False)

    def published(self):
        return self.get_query_set().published()

    def todays_events(self):
        return self.get_query_set().todays_events()


class Event(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)
    title = models.CharField(max_length=250, blank=True)
    title_not_announced = models.BooleanField(default=False, verbose_name="Title to be announced")
    slug = models.SlugField()
    description = models.TextField(blank=True)
    person_set = models.ManyToManyField(Person, through=PersonEvent, blank=True)
    audience = models.TextField(verbose_name="Who can attend", choices=AUDIENCE_CHOICES, default=AUDIENCE_OXFORD)
    booking_type = models.TextField(verbose_name="Booking required",
                                    choices=BOOKING_CHOICES,
                                    default=BOOKING_NOT_REQUIRED)
    booking_url = models.URLField(blank=True, default='',
                                  verbose_name="Web address for booking")
    cost = models.TextField(blank=True, default='', verbose_name="Cost", help_text="If applicable")
    status = models.TextField(verbose_name="Status",
                              choices=EVENT_STATUS_CHOICES,
                              default=EVENT_IN_PREPARATION)
    # embargo: used by administrators to block a talk from being published
    embargo = models.BooleanField(default=False,
                                  verbose_name="Embargo")
    special_message = models.TextField(
        blank=True,
        default='',
        verbose_name="Special message",
        help_text="Use this for important notices - e.g.: cancellation or a last minute change of venue."
    )
    group = models.ForeignKey(EventGroup, null=True, blank=True,
                              related_name='events')
    location = models.TextField(blank=True)
    location_details = models.TextField(blank=True,
                                        default='',
                                        verbose_name='Additional details',
                                        help_text='e.g.: room number or accessibility information')
    # TODO I'm guessing an event can be organised by multiple departments?
    department_organiser = models.TextField(default='', blank=True)

    topics = GenericRelation(TopicItem)

    objects = EventManager()
    _cached_resources = {}

    @property
    def speakers(self):
        return self.person_set.filter(personevent__role=ROLES_SPEAKER)

    @property
    def organizers(self):
        return self.person_set.filter(personevent__role=ROLES_ORGANIZER)

    @property
    def hosts(self):
        return self.person_set.filter(personevent__role=ROLES_HOST)

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
            self.slug = slugify(self.title)  # FIXME max_length, empty title
        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Event: {title} ({start})".format(title=self.title, start=self.start)

    def get_absolute_url(self):
        return reverse('show-event', args=[str(self.id)])

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


reversion.register(Event)
reversion.register(EventGroup)
reversion.register(Person)
reversion.register(PersonEvent)
reversion.register(TopicItem)
