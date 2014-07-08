# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from contextlib import closing
from email.utils import formataddr

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.template.loader import render_to_string
from django.utils.encoding import force_text

from pyconde.celery import app

from ..conference.models import current_conference
from .utils import SEND_MAIL_FILTERS, get_addressed_as


LOG = logging.getLogger(__name__)


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


@app.task(ignore_result=True)
def sendmail_task(target, subject, message, domain):
    users = User.objects.select_related('profile').all()
    users = SEND_MAIL_FILTERS[target](users)

    prefix = '[%s]' % force_text(current_conference())
    if not subject.startswith(prefix):
        subject = '%s %s' % (prefix, subject)

    base_message = message.replace('$$CONFERENCE$$',
                                   force_text(current_conference())) \
                          .replace('$$DOMAIN$$', domain)
    base_message = render_to_string('accounts/emails/sendmail.txt', {
        'conference': current_conference(),
        'message': base_message,
    })

    # Re-use the connection to the server, so that a connection is not
    # implicitly created for every mail, as described in the docs:
    # https://docs.djangoproject.com/en/dev/topics/email/#sending-multiple-emails
    for i, userset in enumerate(chunks(users, 50)):
        sendmail_task_users.delay(userset, subject, base_message)
        LOG.info('Delayed sendmail_task_users {0}'.format(i))


@app.task(ignore_result=True)
def sendmail_task_users(users, subject, base_message):
    with closing(mail.get_connection()) as connection:
        for i, user in enumerate(users):
            try:
                addressed_as = get_addressed_as(user)
                body = base_message.replace('$$RECEIVER$$', addressed_as)
                to = formataddr((addressed_as, user.email))
                email = mail.EmailMessage(subject, body, to=[to],
                    headers={'Reply-To': settings.SUPPORT_EMAIL},
                    connection=connection
                )
                email.send()
            except Exception as e:
                LOG.error('Error sending mail "{0}" to "{1}": {2}'.format(subject, user, e))
