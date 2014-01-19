from django.conf import settings


INVOICE_NUMBER_SEQUENCE_NAME = getattr(settings,
                                       'PURCHASE_INVOICE_NUMBER_SEQUENCE_NAME',
                                       'invoice_number')
