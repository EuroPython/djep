from cms.menu_bases import CMSAttachMenu
from menus.menu_pool import menu_pool
from menus.base import NavigationNode

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class ProposalsMenu(CMSAttachMenu):
    name = _("Proposals menu")

    def get_nodes(self, request):
        nodes = []
        if request.user.is_authenticated():
            nodes.append(NavigationNode(
                _("My proposals"), reverse('my_proposals'), "proposals-mine"
                ))
            nodes.append(NavigationNode(
                _("Submit"), reverse('submit_proposal'), "proposals-submit"
                ))
        return nodes

menu_pool.register_menu(ProposalsMenu)
