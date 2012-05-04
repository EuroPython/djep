from django.contrib import admin

from . import models


admin.site.register(models.Event,
    list_display=['date', 'title', 'conference'],
    list_filter=['conference'])
