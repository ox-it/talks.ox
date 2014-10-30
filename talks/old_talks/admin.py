from django.contrib import admin

from .models import OldTalk, OldSeries


class OldTalkAdmin(admin.ModelAdmin):
    list_display = ('old_talk_id', 'event')


class OldSeriesAdmin(admin.ModelAdmin):
    list_display = ('old_series_id', 'group')


admin.site.register(OldTalk, OldTalkAdmin)
admin.site.register(OldSeries, OldSeriesAdmin)
