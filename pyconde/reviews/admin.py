# -*- encoding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ..speakers import models as speaker_models

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


class CommentAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentAdminForm, self).__init__(*args, **kwargs)
        proposals = self.fields['proposal'].queryset.select_related('conference') \
                                                    .only('title', 'conference')
        versions = self.fields['proposal_version'].queryset.select_related('original') \
                                                  .only('original__title', 'pub_date')
        self.fields['proposal'].queryset = proposals
        self.fields['proposal_version'].queryset = versions


class ReviewMetaDataAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReviewMetaDataAdminForm, self).__init__(*args, **kwargs)
        proposals = self.fields['proposal'].queryset.select_related('conference') \
                                                    .only('title', 'conference')
        versions = self.fields['latest_proposalversion'].queryset \
                                                  .select_related('original') \
                                                  .only('original__title', 'pub_date')
        self.fields['proposal'].queryset = proposals
        self.fields['latest_proposalversion'].queryset = versions


class ProposalVersionAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProposalVersionAdminForm, self).__init__(*args, **kwargs)
        speakers = speaker_models.Speaker.objects.get_qs_for_formfield()
        proposals = self.fields['original'].queryset.select_related('conference') \
                                                    .only('title',
                                                          'conference__title')
        self.fields['speaker'].queryset = speakers
        self.fields['additional_speakers'].queryset = speakers
        self.fields['original'].queryset = proposals


class ReviewAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReviewAdminForm, self).__init__(*args, **kwargs)
        proposals = self.fields['proposal'].queryset.select_related('conference') \
                                                    .only('title', 'conference')
        versions = self.fields['proposal_version'].queryset.select_related('original') \
                                                  .only('original__title', 'pub_date')
        self.fields['proposal'].queryset = proposals
        self.fields['proposal_version'].queryset = versions


class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    actions = [mark_comment_as_deleted]
    list_display = ['proposal', 'author', 'pub_date', 'deleted']
    list_filter = ['deleted']


class ProposalMetaDataAdmin(admin.ModelAdmin):
    actions = [export_reviewed_proposals]
    form = ReviewMetaDataAdminForm
    list_display = ['proposal', 'num_comments', 'num_reviews',
        'latest_activity_date', 'score']


class ProposalVersionAdmin(admin.ModelAdmin):
    form = ProposalVersionAdminForm
    list_display = ['original', 'pub_date', 'creator']


class ReviewerAdmin(admin.ModelAdmin):
    actions = [accept_reviewer_request, decline_reviewer_request]
    list_display = ['user', 'user_display_name', 'user_email', 'state',
        'link_profile']
    list_filter = ['state']
    search_fields = ('user__username',)

    def user_display_name(self, instance):
        return instance.user.profile.display_name

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


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'user', 'rating', 'pub_date']
    actions = [export_reviews]
    form = ReviewAdminForm


admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.ProposalMetaData, ProposalMetaDataAdmin)
admin.site.register(models.ProposalVersion, ProposalVersionAdmin)
admin.site.register(models.Review, ReviewAdmin)
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
