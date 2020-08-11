from __future__ import absolute_import
from django.dispatch import Signal

# signal used when an Event has been created or updated
event_updated = Signal(providing_args=['instance'])

# signal used when an EventGroup has been created or updated
eventgroup_updated = Signal(providing_args=['instance'])
