from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import Event, EventGroup, Person, TopicItem


class TopicItemInlineAdmin(GenericStackedInline):
    model = TopicItem


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')
    inlines = [TopicItemInlineAdmin]

    """
        Customise permissions for who is allowed to edit the event. Permissions are defined by
    """
    def has_change_permission(self, request, obj=None):
        # allow change permission if the user is in the list of editors
        return self.is_event_editor(request.user, obj)

    def has_delete_permission(self, request, obj=None):
        return self.is_event_editor(request.user, obj)

    def is_event_editor(self, user, obj):
        if user.is_superuser:
            return True;
        elif obj is None:
            return True;
        else:
            return obj.editor_set.filter(id=user.id).exists();



class PersonAdmin(admin.ModelAdmin):
    list_display = ('name',)


class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
