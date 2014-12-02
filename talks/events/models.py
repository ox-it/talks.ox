import logging
import functools
from datetime import date
import uuid

import requests
import reversion
from textile import textile_restricted

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.template.defaultfilters import date as date_filter
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from talks.api_ox.api import ApiException, OxfordDateResource


logger = logging.getLogger(__name__)

ROLES_SPEAKER = 'speaker'
ROLES_HOST = 'host'
ROLES_ORGANISER = 'organiser'
ROLES = (
    (ROLES_SPEAKER, 'Speaker'),
    (ROLES_HOST, 'Host'),
    (ROLES_ORGANISER, 'Organiser'),
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

EVENT_PUBLISHED = 'published'
EVENT_IN_PREPARATION = 'preparation'
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
    organiser = models.ForeignKey("Person", null=True, blank=True)
    occurence = models.TextField(
        blank=True,
        default='',
        verbose_name='Timing',
        help_text='e.g.: Mondays at 10 or September 19th to 20th.'
    )
    web_address = models.URLField(blank=True, default='', verbose_name='Web address')
    department_organiser = models.TextField(default='', blank=True)

    objects = EventGroupManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('show-event-group', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = str(uuid.uuid4())
        super(EventGroup, self).save(*args, **kwargs)

    @property
    def api_organisation(self):
        from . import forms
        try:
            return forms.DEPARTMENT_DATA_SOURCE.get_object_by_id(self.department_organiser)
        except requests.HTTPError:
            return None

class PersonManager(models.Manager):

    def suggestions(self, query):
        return self.filter(name__icontains=query)


class Person(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    bio = models.TextField()
    email_address = models.EmailField(max_length=254)

    objects = PersonManager()

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = str(uuid.uuid4())
        super(Person, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('show-person', args=[self.slug])

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


class PublishedEventManager(models.Manager):
    """Manager filtering events not publised
    or in preparation.
    """

    def get_query_set(self):
        return super(PublishedEventManager, self).get_query_set().filter(embargo=False,
                                                                         status=EVENT_PUBLISHED)


class Event(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)
    title = models.CharField(max_length=250, blank=True)
    title_not_announced = models.BooleanField(default=False, verbose_name="Title to be announced")
    slug = models.SlugField()
    description = models.TextField(blank=True)
    person_set = models.ManyToManyField(Person, through=PersonEvent, blank=True)
    editor_set = models.ManyToManyField(User, blank=True)
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
    department_organiser = models.TextField(default='', blank=True)

    topics = GenericRelation(TopicItem)

    objects = models.Manager()
    # manager used to only get published, non embargo events
    published = PublishedEventManager()

    _cached_resources = {}

    @property
    def speakers(self):
        return self.person_set.filter(personevent__role=ROLES_SPEAKER)

    @property
    def organisers(self):
        return self.person_set.filter(personevent__role=ROLES_ORGANISER)

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
        from . import forms
        try:
            return forms.LOCATION_DATA_SOURCE.get_object_by_id(self.location)
        except requests.HTTPError:
            return None

    @property
    def api_organisation(self):
        from . import forms
        try:
            return forms.DEPARTMENT_DATA_SOURCE.get_object_by_id(self.department_organiser)
        except requests.HTTPError:
            return None

    @property
    def api_topics(self):
        from . import forms
        uris = [item.uri for item in self.topics.all()]
        logging.debug("uris:%s", uris)
        try:
            return forms.TOPICS_DATA_SOURCE.get_object_list(uris)
        except requests.HTTPError:
            return None

    @property
    def oxford_date(self):
        if not self.start:
            return None
        func = functools.partial(OxfordDateResource.from_date, self.start)
        return self.fetch_resource(self.start, func)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = str(uuid.uuid4())
        super(Event, self).save(*args, **kwargs)

    @property
    def description_html(self):
        return textile_restricted(self.description)

    def __unicode__(self):
        return u"Event: {title} ({start})".format(title=self.title, start=self.start)

    def get_absolute_url(self):
        return reverse('show-event', args=[str(self.slug)])

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

    @property
    def is_published(self):
        """Check if the event is published (i.e. not embargo)
        :return: True if the Event is published else False
        """
        if self.embargo:
            return False
        elif self.status == EVENT_IN_PREPARATION:
            return False
        elif self.status == EVENT_PUBLISHED:
            return True
        else:
            return False


    def user_can_edit(self, user):
        """
        Check if the given django User is authorised to edit this event.
        They need to have the events.change_event permission AND be in the event's editors_set, or be a superuser
        :param user: The django user wishing to edit the event
        :return: True if the user is allowed to edit this event, False otherwise
        """
        return self.editor_set.filter(id=user.id).exists() or user.is_superuser


reversion.register(Event)
reversion.register(EventGroup)
reversion.register(Person)
reversion.register(PersonEvent)
reversion.register(TopicItem)
