# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def generate_badge(data):
    try:
        from badge_exporter import BadgeMaker, PAGE_SIZE, registerAdditionalFonts
    except ImportError:
        return None

    registerAdditionalFonts(settings.PURCHASE_INVOICE_FONT_ROOT)
    ps = PAGE_SIZE[0], PAGE_SIZE[1] * 2
    bm = BadgeMaker(ps, 'dummy.pdf', rotate=True)
    d = []
    for t in data:
        d.extend([t, t])
    return bm.createBadges(d)
