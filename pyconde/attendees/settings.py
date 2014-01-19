from django.conf import settings


INVOICE_NUMBER_SEQUENCE_NAME = getattr(settings,
                                       'PURCHASE_INVOICE_NUMBER_SEQUENCE_NAME',
                                       'invoice_number')
INVOICE_NUMBER_FORMAT = getattr(settings,
                                'PURCHASE_INVOICE_NUMBER_FORMAT',
                                '{0}')
PRODUCT_NUMBER_START = getattr(settings, 'ATTENDEES_PRODUCT_NUMBER_START', 1)
