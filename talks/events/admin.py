from django.contrib import admin

from .models import Event, EventGroup, Speaker, Location


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name',)


admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Location, LocationAdmin)
