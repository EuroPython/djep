# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


def generate_token():
    return str(uuid4())

def gen_confirm_expire_date():
    return datetime.now() + timedelta(days=2)


class Profile(models.Model):
    user = models.OneToOneField(User)
    short_info = models.TextField('Steckbrief', blank=True)


class EmailVerification(models.Model):
    user = models.ForeignKey(User, verbose_name='User', blank=False)
    old_email = models.EmailField('Alte Adresse')
    new_email = models.EmailField('neue Adresse')

    token = models.CharField('Token', max_length=40, default=generate_token)
    code = models.CharField('Code', max_length=40, default=generate_token)
    is_approved = models.BooleanField('Bestätigt', default=False)
    is_expired = models.BooleanField('Abgelaufen', default=False)
    expiration_date = models.DateTimeField('Ablaufdatum', default=gen_confirm_expire_date)

    def __unicode__(self):
        return '%s - %s/%s' % (self.user, self.old_email, self.new_email)

    def save(self, *args, **kwargs):
        if self.is_approved:
            EmailVerification.objects.filter(
                user=self.user, is_approved=False).update(is_expired=True)
            self.is_expired = True
            if self.user.email == self.old_email:
                self.user.email = self.new_email
                self.user.save()
        return super(EmailVerification, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'E-Mail Bestätigung'
        verbose_name_plural = 'E-Mail Bestätigungen'
