from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool


class SponsorshipMenu(CMSAttachMenu):
    name = _("Sponsorship Menu")

    def get_nodes(self, request):
        nodes = []
        if request.user.has_perm('sponsorship.add_joboffer'):
            nodes.append(NavigationNode(_('Send job offer'), reverse('sponsorship_send_job_offer'), 'sponsorship_send_job_offer'))
        return nodes

menu_pool.register_menu(SponsorshipMenu)
