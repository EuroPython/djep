# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import groupby

from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models 

class SponsorListPlugin(CMSPluginBase):
    model = models.SponsorListPlugin
    name = _("Sponsor list plugin")
    render_template = "cms/plugins/sponsorship/list.html"

    def render(self, context, instance, placeholder):
        levels = instance.levels.order_by('order').all()
        sponsors = models.Sponsor.objects.filter(
            level__in=levels, active=True).order_by('level__order')\
            .select_related('level')
        groups = None
        sublists = None
        if instance.group:
            groups = [(k, list(v)) for k, v in groupby(sponsors, key=lambda x: x.level)]
        elif instance.split_list_length is not None:
            sponsor_list = list(sponsors)
            # partition sponsors list: http://stackoverflow.com/a/1751478
            sublists = [sponsor_list[i:i+instance.split_list_length] for i in range(0, len(sponsor_list), instance.split_list_length)]
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'sponsors': sponsors,
            'groups': groups,
            'sublists': sublists
            })
        return context

plugin_pool.register_plugin(SponsorListPlugin)
