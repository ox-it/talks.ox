from __future__ import absolute_import
from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from talks.users.models import TalksUser, Collection, TalksUserCollection


class TalksUserInline(admin.StackedInline):
    model = TalksUser
    can_delete = False


def is_contributor(user):
    if ("Contributors" in user.groups.values_list('name', flat=True)):
        return True
    else:
        return False

class UserAdmin(UserAdmin):

    inlines = (TalksUserInline, )

    is_contributor.boolean = True
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', is_contributor)
    



class TalksUserCollectionAdmin(admin.ModelAdmin):
    # allow changing of list owner for public lists
    list_display = ('collection', 'user')
    readonly_fields = ('collection', )
    fieldsets = (
        ( 'Collection Owner', {
            'fields' : ('collection', 'user')
        })
    , )

    
    def get_queryset(self, request):
        # only show owner relationships for public talks
        qs = super(TalksUserCollectionAdmin, self).get_queryset(request)
        return qs.filter(role='owner').filter(collection__public=True)

admin.site.register(TalksUserCollection, TalksUserCollectionAdmin)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
