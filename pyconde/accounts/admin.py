from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from . import models


class ProfileAdminForm(forms.ModelForm):

    badge_status_form = forms.MultipleChoiceField(label=_('Badge status'),
        required=False, choices=models.PROFILE_BADGE_STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = models.Profile
        exclude = ['badge_status']

    def __init__(self, *args, **kwargs):
        super(ProfileAdminForm, self).__init__(*args, **kwargs)
        self.fields['badge_status_form'].initial = self.instance.badge_status_list

    def save(self, commit=True):
        self.instance.badge_status = ','.join(self.cleaned_data['badge_status_form'])
        return super(ProfileAdminForm, self).save(commit=commit)


class WithChildrenFilter(SimpleListFilter):
    title = _('Attending with children')
    parameter_name = 'children'

    def lookups(self, request, model_admin):
        return (('y', _('with children')),
                ('n', _('without children')))

    def queryset(self, request, queryset):
        if self.value() == 'y':
            queryset = queryset.filter(num_accompanying_children__gt=0)
        elif self.value() == 'n':
            queryset = queryset.filter(num_accompanying_children=0)
        return queryset


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('pk', 'user', 'display_name', 'full_name',
                    'accept_pysv_conferences', 'accept_ep_conferences',
                    'twitter', 'organisation')
    list_display_links = ('pk', 'user')
    list_filter = (WithChildrenFilter, 'accept_pysv_conferences',
                   'accept_ep_conferences')
    search_fields = ('user__username', 'full_name', 'display_name', 'twitter')


admin.site.register(models.Profile, ProfileAdmin)
