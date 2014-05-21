from django.contrib import admin

from .models import Event, Series, Talk, Speaker, Location


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('oxpoints_id', 'name',)


admin.site.register(Event, EventAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Talk, EventAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Location, LocationAdmin)
