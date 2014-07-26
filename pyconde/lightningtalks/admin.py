from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from . import models

class HasSlidesFilter(admin.SimpleListFilter):
    title = _('has slides')
    parameter_name = 'slides'

    def lookups(self, request, model_admin):
        return (
            ('y', _('Yes')),
            ('n', _('No'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return queryset.filter(slides_url__isnull=False).exclude(slides_url='')
        elif self.value() == 'n':
            return queryset.filter(Q(slides_url__isnull=True) | Q(slides_url=''))
        return queryset


class LightningTalkAdmin(admin.ModelAdmin):
    list_display = ['title',]
    raw_id_fields = ('speakers',)
    list_filter = (
        HasSlidesFilter,
    )

admin.site.register(models.LightningTalk, LightningTalkAdmin)