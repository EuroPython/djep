# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag(takes_context=True)
def highlight(context, value):
    if any(term in force_text(value) for term in context['search_terms']):
        value = format_html('<strong>{0}</strong>', value)
    return value
