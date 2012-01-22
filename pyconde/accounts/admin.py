# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import EmailVerification, Profile


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'old_email', 'new_email', 'expiration_date',
                    'is_approved', 'is_expired')
    list_filter = ('is_approved', 'is_expired')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(Profile, ProfileAdmin)
