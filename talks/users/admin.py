from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from talks.users.models import TalksUser


class TalksUserInline(admin.StackedInline):
    model = TalksUser
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = (TalksUserInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
