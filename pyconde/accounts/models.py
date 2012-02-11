# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User)
    short_info = models.TextField('Steckbrief', blank=True)
