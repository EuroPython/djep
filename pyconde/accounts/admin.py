from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from . import models


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
    list_display = ('pk', 'user', 'display_name', 'full_name',
                    'accept_pysv_conferences', 'accept_ep_conferences',
                    'twitter', 'organisation')
    list_display_links = ('pk', 'user')
    list_filter = (WithChildrenFilter, 'accept_pysv_conferences',
                   'accept_ep_conferences')
    search_fields = ('user__username', 'full_name', 'display_name', 'twitter')


admin.site.register(models.Profile, ProfileAdmin)
