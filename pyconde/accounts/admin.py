from django.contrib import admin

from . import models


admin.site.register(models.Profile,
    list_display=['user'])
