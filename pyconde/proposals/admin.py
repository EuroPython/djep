from django.contrib import admin

from . import models


class ProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "conference", "duration", "speaker", "track")
    list_filter = ("conference", "kind", "duration", "track")


admin.site.register(models.Proposal, ProposalAdmin)
