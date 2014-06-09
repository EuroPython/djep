# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .forms import CMSStaffListPluginForm
from .models import Profile, StaffListPlugin, PROFILE_BADGE_STATUS_CHOICES


first_element = itemgetter(0)


class CMSStaffListPlugin(CMSPluginBase):

    form = CMSStaffListPluginForm
    model = StaffListPlugin
    name = _('Staff list')
    render_template = 'accounts/plugins/staff_list.html'

    def render(self, context, instance, placeholter):
        filter_list = instance.badge_status_list
        profiles = list(Profile.objects
                               .filter(badge_status__in=filter_list)
                               .values_list('display_name',
                                            'user_id',  # profile URL points to UID
                                            'avatar')
                               .all())
        names = [(n, None, None) for n in instance.additional_names_list]
        sorted_names = sorted(profiles + names, key=first_element)
        context.update({
            'names': sorted_names
        })
        return context

plugin_pool.register_plugin(CMSStaffListPlugin)
