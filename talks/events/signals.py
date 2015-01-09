from django.dispatch import Signal

# signal used when an event has been created or updated
event_updated = Signal(providing_args=['instance'])
