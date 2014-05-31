from django import forms
from django.contrib import admin

from ..speakers import models as speaker_models

from . import models

class ProposalAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProposalAdminForm, self).__init__(*args, **kwargs)
        speakers = speaker_models.Speaker.objects.get_qs_for_formfield()
        self.fields['speaker'].queryset = speakers
        self.fields['additional_speakers'].queryset = speakers

    def clean_location(self):
        if not self.cleaned_data['location']:
            raise forms.ValidationError(ugettext('The location is mandatory.'))
        return self.cleaned_data['location']


class ProposalAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "conference", "duration", "speaker", "track")
    list_filter = ("conference", "kind", "duration", "track")
    form = ProposalAdminForm

    def queryset(self, request):
        qs = super(ProposalAdmin, self).queryset(request)
        view = getattr(self, 'view', None)
        if view == 'list':
            qs = qs.select_related(
                'conference', 'kind', 'duration', 'track',
                'speaker__user__profile') \
            .only('title',
                  'kind__name',
                  'conference__title',
                  'duration__label', 'duration__minutes',
                  'speaker__user__profile__display_name',
                  'speaker__user__profile__full_name',
                  'speaker__user__profile__user',
                  'speaker__user__username',
                  'track__name')
        elif view == 'form':
            qs = qs.select_related(
                'conference', 'kind', 'duration', 'track', 'location',
                'speaker__user__profile', 'additional_speakers__user__profile',
                'available_timeslots'
            )
        return qs

    def add_view(self, *args, **kwargs):
        self.view = 'form'
        return super(ProposalAdmin, self).add_view(*args, **kwargs)

    def changelist_view(self, *args, **kwargs):
        self.view = 'list'
        return super(ProposalAdmin, self).changelist_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.view = 'form'
        return super(ProposalAdmin, self).change_view(*args, **kwargs)


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'slot', 'section')


admin.site.register(models.Proposal, ProposalAdmin)
admin.site.register(models.TimeSlot, TimeSlotAdmin)
