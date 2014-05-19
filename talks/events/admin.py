from django.contrib import admin

from .models import Event, Series, Talk, Speaker


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(Event, EventAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Talk, EventAdmin)
admin.site.register(Speaker, SpeakerAdmin)
