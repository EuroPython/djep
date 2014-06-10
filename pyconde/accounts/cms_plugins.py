# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import Profile, UserListPlugin


first_element = itemgetter(0)


class CMSUserListPlugin(CMSPluginBase):

    model = UserListPlugin
    name = _('User list')
    render_template = 'accounts/plugins/user_list.html'

    def render(self, context, instance, placeholter):
        filter_list = instance.badge_status.values_list('id', flat=True)
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

plugin_pool.register_plugin(CMSUserListPlugin)
