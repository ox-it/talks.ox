from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import Event, EventGroup, Person, TopicItem


class TopicItemInlineAdmin(GenericStackedInline):
    model = TopicItem


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')
    inlines = [TopicItemInlineAdmin]


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name',)


class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
