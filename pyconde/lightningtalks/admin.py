from django.contrib import admin

from . import models


class LightningTalkAdmin(admin.ModelAdmin):
    list_display = ['title',]
    raw_id_fields = ('speakers',)

admin.site.register(models.LightningTalk, LightningTalkAdmin)