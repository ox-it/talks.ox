from django.contrib import admin

from .models import OldTalk, OldSeries


admin.site.register(OldTalk, admin.ModelAdmin)
admin.site.register(OldSeries, admin.ModelAdmin)
