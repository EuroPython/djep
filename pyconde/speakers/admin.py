from django.contrib import admin

from pyconde.accounts import utils as account_utils

from . import models


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_name')
    search_fields = ('user__username', 'user__profile__full_name', 'user__profile__display_name')

    def queryset(self, request):
        qs = super(SpeakerAdmin, self).queryset(request)
        return qs.select_related('speaker__user__profile')

    def get_name(self, instance):
        return account_utils.get_display_name(instance.user)
    get_name.short_description = 'Name'

admin.site.register(models.Speaker, SpeakerAdmin)
