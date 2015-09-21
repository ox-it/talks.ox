from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from talks.users.models import TalksUser


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

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
