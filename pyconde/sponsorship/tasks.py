from contextlib import closing

from django.core import mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

from pyconde.sponsorship.models import JobOffer
from pyconde.accounts.models import Profile

from pyconde.celery import app


@app.task(ignore_result=True)
def send_job_offer(job_offer_id):

    try:
        offer = JobOffer.objects.select_related('sponsor').get(pk=job_offer_id)
    except JobOffer.DoesNotExit:
        raise RuntimeError('No job offer found with pk %d' % job_offer_id)

    profiles = Profile.objects.filter(accept_job_offers=True).select_related('user')

    with closing(mail.get_connection()) as connection:
        offset = 0
        while True:
            chunk = profiles[offset:offset+50]
            offset += 50
            if not chunk:
                break
            body = render_to_string('sponsorship/emails/job_offer.txt', {
                'offer': offer,
                'site': Site.objects.get_current()
            })
            email = mail.EmailMessage(offer.subject, body,
                bcc=[profile.user.email for profile in chunk],
                headers={'Reply-To': offer.reply_to},
                connection=connection
            )
            email.send()
