from django.conf import settings


REMINDER_DUE_DATE_OFFSET = getattr(settings,
                                   'PAYMENT_REMINDER_DUE_DATE_OFFSET',
                                   14)
