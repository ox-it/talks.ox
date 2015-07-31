import itertools
import uuid

from textile import textile_restricted

from django.db import models
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from talks.events.models import Event, EventGroup


DEFAULT_COLLECTION_NAME = "My Collection"
COLLECTION_ROLES_OWNER = 'owner'
COLLECTION_ROLES_EDITOR = 'editor'
COLLECTION_ROLES_READER = 'reader'
COLLECTION_ROLES = (
    (COLLECTION_ROLES_OWNER, 'Owner'),
    (COLLECTION_ROLES_EDITOR, 'Collaborator'),
    (COLLECTION_ROLES_READER, 'Viewer'),
)

class Collection(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    editor_set = models.ManyToManyField('TalksUser', through='TalksUserCollection', blank=True)
    public = models.BooleanField(default=False)

    # TODO list private or public/shared?

    def _get_items_by_model(self, model):
        """Used when selecting a particular type (specified in the `model` arg)
        of objects from our Collection.

            1) Get the ContentType for that `model`
            2) Filter to the CollectionItems of that ContentType and get all
               `object_id`s
            3) Select these `object_id`s from the `model`
        """
        content_type = ContentType.objects.get_for_model(model)
        ids = self.collectionitem_set.filter(content_type=content_type
                                             ).values_list('object_id')
        return model.objects.filter(id__in=itertools.chain.from_iterable(ids))

    class ItemAlreadyInCollection(Exception):
        pass

    class InvalidItemType(Exception):
        pass

    def get_absolute_url(self):
        return reverse('view-list', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            # Newly created object, so set slug
            self.slug = str(uuid.uuid4())

        super(Collection, self).save(*args, **kwargs)

    def add_item(self, item):
        if isinstance(item, Event):
            # Adding an event
            content_type = ContentType.objects.get_for_model(Event)
        elif isinstance(item, EventGroup):
            # Adding event group
            content_type = ContentType.objects.get_for_model(EventGroup)
        else:
            raise self.InvalidItemType()
        try:
            self.collectionitem_set.get(content_type=content_type,
                                        object_id=item.id)
            raise self.ItemAlreadyInCollection()
        except CollectionItem.DoesNotExist:
            item = self.collectionitem_set.create(item=item)
            return item

    def remove_item(self, item):
        if isinstance(item, Event):
            content_type = ContentType.objects.get_for_model(Event)
        elif isinstance(item, EventGroup):
            content_type = ContentType.objects.get_for_model(EventGroup)
        else:
            raise self.InvalidItemType()
        try:
            item = self.collectionitem_set.get(content_type=content_type,
                                               object_id=item.id)
            item.delete()
            return True
        except CollectionItem.DoesNotExist:
            return False

    def get_events(self):
        return self._get_items_by_model(Event)

    def get_event_groups(self):
        return self._get_items_by_model(EventGroup)

    def get_all_events(self):
        """
          Returns all distinct events in this collections events and event groups:
        """
        eventIDs = self.collectionitem_set.filter(content_type=ContentType.objects.get_for_model(Event)
                                             ).values_list('object_id')
        eventGroupIDs = self.collectionitem_set.filter(content_type=ContentType.objects.get_for_model(EventGroup)
                                             ).values_list('object_id')
        events = Event.objects.filter(id__in=itertools.chain.from_iterable(eventIDs))
        eventsInEventGroups = Event.objects.filter(group=eventGroupIDs)

        allEvents = events | eventsInEventGroups

        return allEvents.distinct().order_by('start')

    def contains_item(self, item):
        if isinstance(item, Event):
            content_type = ContentType.objects.get_for_model(Event)
        elif isinstance(item, EventGroup):
            content_type = ContentType.objects.get_for_model(EventGroup)
        else:
            raise self.InvalidItemType()
        try:
            self.collectionitem_set.get(content_type=content_type,
                                        object_id=item.id)
            return True
        except CollectionItem.DoesNotExist:
            return False

    @property
    def description_html(self):
        return textile_restricted(self.description, auto_link=True, lite=False)

    def user_can_edit(self, user):
        return self.editor_set.filter(id=user.id, talksusercollection__role=COLLECTION_ROLES_OWNER).exists() or user.is_superuser

    def __unicode__(self):
        return self.title


class TalksUserCollection(models.Model):
    user = models.ForeignKey("TalksUser")
    collection = models.ForeignKey(Collection)
    role = models.TextField(choices=COLLECTION_ROLES, default=COLLECTION_ROLES_OWNER)
    is_main = models.BooleanField(default=False)



class TalksUser(models.Model):

    user = models.OneToOneField(User)
    collections = models.ManyToManyField(Collection, through=TalksUserCollection, blank=True)

    def save(self, *args, **kwargs):
        super(TalksUser, self).save(*args, **kwargs)
        if self.collections.count() == 0:
            default_collection = Collection.objects.create(title=DEFAULT_COLLECTION_NAME)
            # Link the collection to the user
            TalksUserCollection.objects.create(user=self,
                                            collection=default_collection,
                                            role=COLLECTION_ROLES_OWNER,
                                            is_main=True)

    def __unicode__(self):
        return unicode(self.user)


class CollectionItem(models.Model):

    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    # Currently item can be an Event or EventGroup
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = [('collection', 'content_type', 'object_id')]


class DepartmentFollow(models.Model):
    pass


class LocationFollow(models.Model):
    pass



@receiver(models.signals.post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """If the User has just been created we use a signal to also create a TalksUser
    """
    if created:
        tuser, tuser_created = TalksUser.objects.get_or_create(user=instance)
