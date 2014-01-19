# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyconde.celery import app


@app.task
def render_invoice(*args, **kwargs):
    send_invoice.delay()


@app.task
def send_invoice(*args, **kwargs):
    pass
