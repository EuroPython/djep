# -*- encoding: utf-8 -*-
import datetime

from django.contrib import admin
from django.http import HttpResponse

from . import models
from . import utils


def mark_comment_as_deleted(modeladmin, request, queryset):
    queryset.update(deleted=True, deleted_date=datetime.datetime.now(), deleted_by=request.user)
mark_comment_as_deleted.short_description = u"Kommentar(e) als gelöscht markieren"


def export_reviews(modeladmin, request, queryset):
    return HttpResponse(utils.create_reviews_export(queryset).csv, mimetype='text/csv')
export_reviews.short_description = u"Als CSV exportieren"


admin.site.register(models.ProposalVersion,
    list_display=['original', 'pub_date', 'creator'])
admin.site.register(models.Review,
    list_display=['proposal', 'user', 'rating', 'pub_date'],
    actions=[export_reviews])
admin.site.register(models.Comment,
    list_display=['proposal', 'author', 'pub_date', 'deleted'],
    list_filter=['deleted'],
    actions=[mark_comment_as_deleted])
admin.site.register(models.ProposalMetaData,
    list_display=['proposal', 'num_comments', 'num_reviews', 'latest_activity_date'])
