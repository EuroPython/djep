# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from . import models
from . import utils


def mark_comment_as_deleted(modeladmin, request, queryset):
    queryset.update(deleted=True, deleted_date=now(), deleted_by=request.user)
mark_comment_as_deleted.short_description = _("Mark comment(s) as deleted")


def export_reviews(modeladmin, request, queryset):
    return HttpResponse(utils.create_reviews_export(queryset).csv, mimetype='text/csv')
export_reviews.short_description = _("Export as CSV")


def export_reviewed_proposals(modeladmin, request, queryset):
    return HttpResponse(utils.create_proposal_score_export(queryset).csv,
        mimetype='text/csv')
export_reviewed_proposals.short_description = _("Export as CSV")


def accept_reviewer_request(modeladmin, request, queryset):
    with commit_on_success():
        perm = utils.get_review_permission()
        for reviewer in queryset.select_related('user').all():
            reviewer.user.user_permissions.add(perm)
        queryset.update(state=models.Reviewer.STATE_ACCEPTED)
        cache.delete('reviewer_pks')
accept_reviewer_request.short_description = _("Accept selected user requests to become a reviewer.")


def decline_reviewer_request(modeladmin, request, queryset):
    with commit_on_success():
        perm = utils.get_review_permission()
        for reviewer in queryset.select_related('user').all():
            reviewer.user.user_permissions.remove(perm)
        queryset.update(state=models.Reviewer.STATE_DECLINED)
        cache.delete('reviewer_pks')
decline_reviewer_request.short_description = _("Decline selected user requests to become a reviewer.")


class ProposalMetaDataAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'num_comments', 'num_reviews',
        'latest_activity_date', 'score']
    actions = [export_reviewed_proposals]

class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_display_name', 'user_email', 'state',
        'link_profile']
    list_filter = ['state']
    actions = [accept_reviewer_request, decline_reviewer_request]
    search_fields = ('user__username',)

    def user_display_name(self, instance):
        return instance.user.get_profile().display_name

    def user_email(self, instance):
        return instance.user.email

    def link_profile(self, instance):
        url = reverse('account_profile', kwargs={'uid': instance.user.pk})
        return '<a href="{url}">{url}</a>'.format(url=url)
    link_profile.allow_tags = True
    link_profile.short_description = _('Link to profile')

    def queryset(self, request):
        qs = super(ReviewerAdmin, self).queryset(request)
        qs = qs.select_related('user__profile')
        return qs


admin.site.register(models.ProposalVersion,
    list_display=['original', 'pub_date', 'creator'])
admin.site.register(models.Review,
    list_display=['proposal', 'user', 'rating', 'pub_date'],
    actions=[export_reviews])
admin.site.register(models.Comment,
    list_display=['proposal', 'author', 'pub_date', 'deleted'],
    list_filter=['deleted'],
    actions=[mark_comment_as_deleted])
admin.site.register(models.ProposalMetaData, ProposalMetaDataAdmin)

admin.site.register(models.Reviewer, ReviewerAdmin)


# Add some more columns and filters to the user admin
class UserAdmin(BaseUserAdmin):
    list_display = list(BaseUserAdmin.list_display) + ['is_superuser', 'is_reviewer']

    def is_reviewer(self, instance):
        return utils.can_review_proposal(instance)
    is_reviewer.boolean = True
    is_reviewer.short_description = _('Can review')

admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)
