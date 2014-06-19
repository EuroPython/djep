from contextlib import closing

from django.core import mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from pyconde.sponsorship.models import JobOffer
from pyconde.accounts.models import Profile

from pyconde.celery import app


@app.task(ignore_result=True)
def send_job_offer(cleaned_data):
    cd = cleaned_data
    profiles = Profile.objects.filter(accept_job_offers=True).select_related('user')
    body = render_to_string('sponsorship/emails/job_offer.txt', {
        'sponsor_name': cd['sponsor'].name,
        'text': cd['text'],
        'site': Site.objects.get_current()
    })

    # Re-use the connection to the server, so that a connection is not
    # implicitly created for every mail, as described in the docs:
    # https://docs.djangoproject.com/en/dev/topics/email/#sending-multiple-emails
    with closing(mail.get_connection()) as connection:
        offset = 0
        while True:
            chunk = profiles[offset:offset+50]
            offset += 50
            if not chunk:
                break
            email = mail.EmailMessage(cd['subject'], body,
                bcc=[profile.user.email for profile in chunk],
                headers={'Reply-To': cd['reply_to']},
                connection=connection
            )
            email.send()
