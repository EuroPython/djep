# -*- encoding: UTF-8 -*-
from cms.menu_bases import CMSAttachMenu
from menus.menu_pool import menu_pool
from menus.base import NavigationNode

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class ScheduleMenu(CMSAttachMenu):
    name = _("Schedule menu")

    def get_nodes(self, request):
        nodes = []
        nodes.append(NavigationNode("Schedule", reverse('schedule'), 'schedule'))
        return nodes

menu_pool.register_menu(ScheduleMenu)
