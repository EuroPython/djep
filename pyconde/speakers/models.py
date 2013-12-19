# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals


class Speaker(models.Model):
    """
    The speaker model acts as user-abstraction for various session and proposal
    related objects.
    """
    user = models.OneToOneField(User, related_name='speaker_profile')

    def __unicode__(self):
        if self.user.first_name and self.user.last_name:
            return "{0} {1}".format(self.user.first_name, self.user.last_name)
        return self.user.username

    def get_absolute_url(self):
        return reverse('account_profile', kwargs={'uid': self.user.id})


def create_speaker_profile(sender, instance, **kwargs):
    """
    Every user also is a potential speaker in the current implemention so we
    also have to create a new speaker object for every newly created user
    instance.
    """
    Speaker.objects.get_or_create(user=instance)

signals.post_save.connect(create_speaker_profile, sender=User, dispatch_uid='speakers.create_speaker_profile')
