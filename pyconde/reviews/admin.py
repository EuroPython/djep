from django.contrib import admin

from . import models


admin.site.register(models.ProposalVersion)
admin.site.register(models.Review)
admin.site.register(models.Comment)