# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from pyconde.speakers import models as speakers_models


class Profile(models.Model):
    user = models.OneToOneField(User)
    short_info = models.TextField(_('short info'), blank=True)


# We also have to create a speaker form for the newly registed user
def create_speaker_profile(sender, instance, created, raw, **kwargs):
    if created:
        speakers_models.Speaker(user=instance).save()

models.signals.post_save.connect(create_speaker_profile, sender=User, dispatch_uid="create_speaker_profile")
