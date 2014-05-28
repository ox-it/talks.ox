from django.db import models


class OxpointsModel(models.Model):
    oxpoints_id = models.CharField(db_index=True,
                                   unique=True,
                                   max_length=50)
    name = models.CharField(max_length=250)

    class Meta:
        abstract = True


class Location(OxpointsModel):
    # TODO what should be stored here? what IS a location?
    # (e.g. building vs actual room of the event)
    # (e.g. additional information, accessibility etc)
    pass


class Organisation(OxpointsModel):
    pass
