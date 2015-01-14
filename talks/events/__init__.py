from django.apps import AppConfig

default_app_config = 'talks.events.EventsConfig'


class EventsConfig(AppConfig):
    name = 'talks.events'
    verbose_name = "Events"

    def ready(self):
        super(EventsConfig, self).ready()
        import talks.events.signals
