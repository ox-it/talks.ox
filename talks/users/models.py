from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TalksUser(models.Model):

    user = models.OneToOneField(User)


@receiver(models.signals.post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """If the User has just been created we use a signal to also create a TalksUser
    """
    if created:
        TalksUser.objects.get_or_create(user=instance)


class Collection(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=250)

    # TODO list private or public/shared?
    # TODO qualify list? (e.g. "Talks I want to attend"?)


class CollectionFollow(models.Model):
    """User following a Collection
    """

    user = models.ForeignKey(TalksUser)
    collection = models.ForeignKey(Collection)
    is_owner = models.BooleanField(default=False)
    # Main/default collection of the user
    is_main = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'collection')


class CollectionItem(models.Model):

    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    # Currently item can be an Event or EventGroup
    item = GenericForeignKey('content_type', 'object_id')


class DepartmentFollow(models.Model):
    pass


class LocationFollow(models.Model):
    pass
