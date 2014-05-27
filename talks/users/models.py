from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TalksUser(models.Model):

    user = models.OneToOneField(User)


class CollectionFollow(models.Model):
    """User following a Collection
    """

    user = models.ForeignKey(TalksUser)
    collection = models.ForeignKey(Collection)
    is_owner = models.BooleanField()
    is_main = models.BooleanField()     # main collection of the user

    class Meta:
        unique_together = ('user', 'collection')


class Collection(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=250)

    # TODO list private or public/shared?
    # TODO qualify list? (e.g. "Talks I want to attend"?)


class CollectionItem(models.Model):

    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')   # atm: Talk, Event, Series


class DepartmentFollow(models.Model):
    pass


class LocationFollow(models.Model):
    pass
