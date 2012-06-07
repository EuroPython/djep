# -*- encoding: utf-8 -*-
import datetime

from django.contrib import admin

from . import models


def mark_comment_as_deleted(modeladmin, request, queryset):
    queryset.update(deleted=True, deleted_date=datetime.datetime.now(), deleted_by=request.user)
mark_comment_as_deleted.short_description = u"Kommentar(e) als gelöscht markieren"

admin.site.register(models.ProposalVersion)
admin.site.register(models.Review)
admin.site.register(models.Comment,
    actions=[mark_comment_as_deleted])
admin.site.register(models.ProposalMetaData,
    list_display=['proposal', 'num_comments', 'num_reviews', 'latest_activity_date'])
