from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from . import models


class WithChildrenFilter(SimpleListFilter):
    title = 'Anzahl Kinder'
    parameter_name = 'children'

    def lookups(self, request, model_admin):
        return (('y', 'mit Kindern'),
                ('n', 'ohne Kinder'))

    def queryset(self, request, queryset):
        if self.value() == 'y':
            queryset = queryset.filter(num_accompanying_children__gt=0)
        elif self.value() == 'n':
            queryset = queryset.filter(num_accompanying_children=0)
        return queryset


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'num_accompanying_children')
    list_display_links = ('pk', 'user')
    list_filter = (WithChildrenFilter,)


admin.site.register(models.Profile, ProfileAdmin)
