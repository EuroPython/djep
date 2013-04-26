from django.contrib import admin

from . import models


class ProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "conference", "duration", "speaker", "track")
    list_filter = ("conference", "kind", "duration", "track")


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'slot', 'section')


admin.site.register(models.Proposal, ProposalAdmin)
admin.site.register(models.TimeSlot, TimeSlotAdmin)
