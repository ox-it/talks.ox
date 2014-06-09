from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import Event, EventGroup, Speaker, Location, Tag, TagItem


class TagItemInlineAdmin(GenericStackedInline):
    model = TagItem


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')
    inlines = [TagItemInlineAdmin,]


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Tag, TagAdmin)
