# -*- coding: utf-8 -*-
# From http://django-configurations.readthedocs.org/en/latest/cookbook/#id4
from __future__ import absolute_import

import os
import logging

from celery import Celery
from celery.signals import task_failure
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyconde.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Base')


from configurations import importer
importer.install()


app = Celery('pyconde')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

logger = logging.getLogger('celery.task')
try:
    from raven.contrib.django.handlers import SentryHandler
    logger.addHandler(SentryHandler())
except ImportError:
    logger.info("No raven/sentry available")


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@task_failure.connect
def process_failure_signal(sender=None, task_id=None, exception=None,
        args=None, kwargs=None, traceback=None, einfo=None, **akwargs):
    # From https://groups.google.com/d/msg/celery-users/lb3_5aAFesA/E1R4TIUiAwgJ
    exc_info = (type(exception), exception, traceback)
    logger.error(
        'Celery job exception: %s (%s)' % (exception.__class__.__name__, exception),
        exc_info=exc_info,
        extra={
            'data': {
                'task_id': task_id,
                'sender': sender,
                'args': args,
                'kwargs': kwargs,
            }
        }
    )
