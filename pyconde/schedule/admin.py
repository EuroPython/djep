from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from ..proposals import models as proposal_models
from ..proposals import admin as proposal_admin
from ..reviews import models as review_models
from ..reviews import admin as review_admin

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
        queryset = queryset.select_related('proposal')
        convert = True
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


class HasSelectedTimeslotsFilter(admin.SimpleListFilter):
    title = _(u'Timeslot Preferences')
    parameter_name = 'ts'

    def lookups(self, request, model_admin):
        return (
            ('y', _(u'with preferences')),
            ('n', _(u'w/o preferences'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return queryset.filter(proposal__available_timeslots__isnull=False).distinct()
        elif self.value() == 'n':
            return queryset.filter(proposal__available_timeslots__isnull=True)
        return queryset


class SessionAdminForm(forms.ModelForm):

    def clean_location(self):
        if not self.cleaned_data['location']:
            raise forms.ValidationError(u'Der Ort muss angegeben werden.')
        return self.cleaned_data['location']


class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "conference", "duration", "speaker", "track", "location",
                    "list_available_timeslots")
    list_filter = ("conference", "kind", "duration", "track", "location",
                   HasSelectedTimeslotsFilter)
    actions = [create_simple_session_export]
    form = SessionAdminForm

    def list_available_timeslots(self, obj):
        return u'; '.join(
            unicode(slot) for slot in obj.proposal.available_timeslots.all())
    list_available_timeslots.short_description = _(u'Timeslot Preferences')


class SideEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'start', 'end', 'conference', 'location']
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
