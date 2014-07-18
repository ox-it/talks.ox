import itertools

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from talks.events.models import Event, EventGroup


DEFAULT_COLLECTION_NAME = "My Collection"


class TalksUser(models.Model):

    user = models.OneToOneField(User)

    @property
    def default_collection(self):
        return self.get_or_create_default_collection()

    def get_or_create_default_collection(self):
        try:
            return CollectionFollow.objects.get(user=self,
                                                is_owner=True,
                                                is_main=True).collection
        except CollectionFollow.DoesNotExist:
            default_collection = Collection.objects.create(
                title=DEFAULT_COLLECTION_NAME)
            # Link the collection to the user
            CollectionFollow.objects.create(user=self,
                                            collection=default_collection,
                                            is_owner=True,
                                            is_main=True)
            return default_collection

    def __unicode__(self):
        return unicode(self.user)


class Collection(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=250)

    # TODO list private or public/shared?
    # TODO qualify list? (e.g. "Talks I want to attend"?)

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

    def __unicode__(self):
        return self.title


class CollectionFollow(models.Model):
    """User following a Collection
    """

    user = models.ForeignKey(TalksUser)
    collection = models.ForeignKey(Collection)
    is_owner = models.BooleanField(default=False)
    # Main/default collection of the user
    is_main = models.BooleanField(default=False)

    class Meta:
        unique_together = [('user', 'collection'),
                           ('user', 'is_main')]


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
        # Talks User has been created
        if tuser_created:
            tuser.get_or_create_default_collection()
