from django.dispatch import Signal
from django.dispatch.dispatcher import receiver

from talks.events.models import Event


# signal used when an event has been created or updated
event_updated = Signal(providing_args=['instance'])


@receiver(event_updated, sender=Event)
def publish_to_old_talks(sender, instance, *args, **kwargs):
    print "RECEIVED SIGNAL EVENT UPDATED"
    from talks.old_talks.tasks import update_old_talks
    update_old_talks(instance)
