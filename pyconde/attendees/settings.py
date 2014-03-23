from django.conf import settings


INVOICE_DISABLE_RENDERING = getattr(settings,
                                    'PURCHASE_INVOICE_DISABLE_RENDERING',
                                    True)

INVOICE_EXPORT_RECIPIENTS = getattr(settings,
                                    'PURCHASE_INVOICE_EXPORT_RECIPIENTS',
                                    [])

INVOICE_FONT_CONFIG = getattr(settings,
                             'PURCHASE_INVOICE_FONT_CONFIG',
                             {'de':{}, 'en': {}})

INVOICE_FONT_ROOT = getattr(settings,
                            'PURCHASE_INVOICE_FONT_ROOT',
                            'fonts/')

INVOICE_NUMBER_FORMAT = getattr(settings,
                                'PURCHASE_INVOICE_NUMBER_FORMAT',
                                'INVOICE-{0:d}')

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

# This defines an excluded minimum value for when a payment mode should
# be made available to the user. For instance an order with the total amount
# of 0 should not offer the creditcard payment mode.
MIN_TOTAL_FOR_PAYMENT_METHOD = getattr(
    settings,
    'ATTENDEES_MIN_TOTAL_FOR_PAYMENT_METHOD',
    {
        'creditcard': 0,
        'invoice': None,
        'elv': None,
    }
)

PAYMENT_METHODS = getattr(settings, 'PAYMENT_METHODS', None)

TERMS_OF_USE_URL = getattr(settings, 'PURCHASE_TERMS_OF_USE_URL', '#')

# With this flag the payment method is hidden if there is just one
# available.
HIDE_SINGLE_PAYMENT_METHOD = getattr(
    settings, 'ATTENDEES_HIDE_SINGLE_PAYMENT_METHOD',
    False)
