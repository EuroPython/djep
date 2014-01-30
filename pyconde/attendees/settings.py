from django.conf import settings


INVOICE_FONT_CONFIG = getattr(settings,
                             'PURCHASE_INVOICE_FONT_CONFIG',
                             {'de':{}, 'en': {}})

INVOICE_FONT_ROOT = getattr(settings,
                            'PURCHASE_INVOICE_FONT_ROOT',
                            'fonts/')

INVOICE_NUMBER_FORMAT = getattr(settings,
                                'PURCHASE_INVOICE_NUMBER_FORMAT',
                                '{0}')

INVOICE_NUMBER_SEQUENCE_NAME = getattr(settings,
                                       'PURCHASE_INVOICE_NUMBER_SEQUENCE_NAME',
                                       'invoice_number')

INVOICE_ROOT = getattr(settings,
                       'PURCHASE_INVOICE_ROOT',
                       'invoices/')

INVOICE_TEMPLATE_PATH = getattr(settings,
                                'PURCHASE_INVOICE_TEMPLATE_PATH',
                                None)

PRODUCT_NUMBER_START = getattr(settings,
                               'ATTENDEES_PRODUCT_NUMBER_START',
                               1)
