from __future__ import unicode_literals
import json

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from ..proposals import models as proposal_models
from ..proposals import admin as proposal_admin
from ..reviews import models as review_models
from ..reviews import admin as review_admin
from ..speakers import models as speaker_models

from . import models
from . import exporters
from . import utils


def schedule_multiple_proposals(modeladmin, request, queryset):
    """
    Converts a queryset of proposals into session objects. If there already
    exists a session for a proposal, it will be skipped.
    """
    proposal_pks = set([o['proposal__id'] for o in models.Session.objects.select_related('proposal').values('proposal__id')])
    counter = 0
    skipped = 0
    convert = False
    if modeladmin.model == review_models.ProposalMetaData:
        queryset = queryset.select_related('proposal').prefetch_related('proposal__tags')
        convert = True
    elif modeladmin.model == proposal_models.Proposal:
        queryset = queryset.prefetch_related('tags')
    for prop in queryset:
        if convert:
            proposal = prop.proposal
        else:
            proposal = prop
        if proposal.pk in proposal_pks:
            skipped += 1
            continue
        models.Session.create_from_proposal(proposal)
        counter += 1
    messages.success(request, _("%(counter)s proposal(s) converted to sessions") % {
        'counter': counter
        })
    if skipped:
        messages.warning(request, _("%(counter)s proposal(s) skipped") % {
            'counter': skipped
        })
schedule_multiple_proposals.short_description = _("convert to sessions")


def create_simple_session_export(modeladmin, request, queryset):
    return HttpResponse(exporters.SimpleSessionExporter(queryset)().csv,
        mimetype='text/csv')
create_simple_session_export.short_description = _("create simple export")


def episodes_export(modeladmin, request, queryset):
    exporter = exporters.SessionForEpisodesExporter()
    return HttpResponse(json.dumps(exporter(), indent=4),
                        mimetype='application/json')
episodes_export.short_description = _("episodes export")


class HasSelectedTimeslotsFilter(admin.SimpleListFilter):
    title = _('Timeslot Preferences')
    parameter_name = 'ts'

    def lookups(self, request, model_admin):
        return (
            ('y', _('with preferences')),
            ('n', _('w/o preferences'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return queryset.filter(proposal__available_timeslots__isnull=False).distinct()
        elif self.value() == 'n':
            return queryset.filter(proposal__available_timeslots__isnull=True)
        return queryset


class SessionAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SessionAdminForm, self).__init__(*args, **kwargs)
        speakers = speaker_models.Speaker.objects.get_qs_for_formfield()
        proposals = self.fields['proposal'].queryset.select_related('conference') \
                                                    .only('title',
                                                          'conference__title')
        self.fields['speaker'].queryset = speakers
        self.fields['additional_speakers'].queryset = speakers
        self.fields['proposal'].queryset = proposals
        self.fields['location'].required = True


class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "conference", "duration", "speaker",
                    "track", "location_pretty", "list_available_timeslots")
    list_filter = ("conference", "kind", "duration", "track", "location",
                   HasSelectedTimeslotsFilter)
    actions = [create_simple_session_export, episodes_export]
    form = SessionAdminForm

    def queryset(self, request):
        qs = super(SessionAdmin, self).queryset(request)
        view = getattr(self, 'view', None)
        if view == 'list':
            qs = qs.select_related('conference', 'kind', 'duration', 'track',
                                   'speaker__user__profile') \
                   .prefetch_related('available_timeslots', 'location') \
                   .only('title',
                         'kind__name',
                         'conference__title',
                         'duration__label', 'duration__minutes',
                         'speaker__user__profile__display_name',
                         'speaker__user__profile__user',
                         'speaker__user__username',
                         'track__name',
                         'location__name')
        elif view == 'form':
            qs = qs.select_related(
                'conference', 'kind', 'duration', 'track', 'location',
                'speaker__user__profile', 'additional_speakers__user__profile',
                'available_timeslots'
            )
        return qs

    def add_view(self, *args, **kwargs):
        self.view = 'form'
        return super(SessionAdmin, self).add_view(*args, **kwargs)

    def changelist_view(self, *args, **kwargs):
        self.view = 'list'
        return super(SessionAdmin, self).changelist_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.view = 'form'
        return super(SessionAdmin, self).change_view(*args, **kwargs)

    def list_available_timeslots(self, obj):
        return '<br />'.join(map(force_text, obj.available_timeslots.all()))
    list_available_timeslots.allow_tags = True
    list_available_timeslots.short_description = _('Timeslot Preferences')


class SideEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'start', 'end', 'conference', 'location_pretty']
    list_filter = ['conference', 'location']


class ProposalAdmin(proposal_admin.ProposalAdmin):
    actions = proposal_admin.ProposalAdmin.actions + [schedule_multiple_proposals]
    list_display = list(proposal_admin.ProposalAdmin.list_display) + ['is_scheduled']

    def is_scheduled(self, instance):
        return utils.proposal_is_scheduled(instance)
    is_scheduled.boolean = True
    is_scheduled.short_description = _("is scheduled")


class ProposalMetaDataAdmin(review_admin.ProposalMetaDataAdmin):
    actions = review_admin.ProposalMetaDataAdmin.actions + [schedule_multiple_proposals]
    list_display = list(review_admin.ProposalMetaDataAdmin.list_display) + ['is_scheduled']

    def is_scheduled(self, instance):
        return utils.proposal_is_scheduled(instance.proposal)
    is_scheduled.boolean = True
    is_scheduled.short_description = _("is scheduled")


admin.site.unregister(review_models.ProposalMetaData)
admin.site.unregister(proposal_models.Proposal)

admin.site.register(models.Session, SessionAdmin)
admin.site.register(proposal_models.Proposal, ProposalAdmin)
admin.site.register(review_models.ProposalMetaData, ProposalMetaDataAdmin)
admin.site.register(models.SideEvent, SideEventAdmin)
