from django.contrib import admin

from .models import JobOffer, Sponsor, SponsorLevel


class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'sponsor', 'active',)
    list_filter=('active',)
    model = JobOffer

admin.site.register(JobOffer, JobOfferAdmin)


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'added', 'active',)
    list_filter=('level', 'active',)
    model = Sponsor

admin.site.register(Sponsor, SponsorAdmin)


class SponsorLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'conference',)
    list_filter=('conference',)
    model = SponsorLevel

admin.site.register(SponsorLevel, SponsorLevelAdmin)
