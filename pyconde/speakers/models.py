# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


class Speaker(models.Model):
    """
    The speaker model acts as user-abstraction for various session and proposal
    related objects.
    """
    user = models.OneToOneField(User, related_name='speaker_profile')

    def __unicode__(self):
        if self.user.first_name and self.user.last_name:
            return u"{0} {1}".format(self.user.first_name, self.user.last_name)
        return self.user.username

    def get_absolute_url(self):
        return reverse('account_profile', kwargs={'uid': self.user.id})


@receiver(post_save, sender=User)
def create_speaker_profile(sender, instance, created, raw, **kwargs):
    """
    Every user also is a potential speaker in the current implemention so we
    also have to create a new speaker object for every newly created user
    instance.
    """
    if created:
        Speaker(user=instance).save()
