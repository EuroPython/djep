from django.contrib import admin

from .models import JobOffer, Sponsor, SponsorLevel


class JobOfferAdmin(admin.ModelAdmin):
    model = JobOffer

admin.site.register(JobOffer, JobOfferAdmin)


class SponsorAdmin(admin.ModelAdmin):
    model = Sponsor
    list_display = ("name", "level", "added", "active")
    list_filter=("level", 'active',)

admin.site.register(Sponsor, SponsorAdmin)


class SponsorLevelAdmin(admin.ModelAdmin):
    model = SponsorLevel

admin.site.register(SponsorLevel, SponsorLevelAdmin)
