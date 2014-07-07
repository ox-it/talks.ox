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

    def _get_items_by_content_type(self, content_type):
        items = self.collectionitem_set.filter(content_type=content_type)
        for item in items:
            yield item.item

    def get_events(self):
        return self._get_items_by_content_type(
            ContentType.objects.get_for_model(Event)
        )

    def get_event_groups(self):
        return self._get_items_by_content_type(
            ContentType.objects.get_for_model(EventGroup)
        )

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
        # TODO: index_together ('user', 'is_main') ?
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
