# -*- coding: utf-8 -*-
# From http://django-configurations.readthedocs.org/en/latest/cookbook/#id4
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyconde.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Base')

from configurations import importer
importer.install()

app = Celery('pyconde')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
