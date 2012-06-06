from django.contrib import admin

from . import models


admin.site.register(models.ProposalVersion)
admin.site.register(models.Review)
admin.site.register(models.Comment)
admin.site.register(models.ProposalMetaData,
    list_display=['proposal', 'num_comments', 'num_reviews', 'latest_activity_date'])
