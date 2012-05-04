from cms.menu_bases import CMSAttachMenu
from menus.menu_pool import menu_pool
from menus.base import NavigationNode

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from conference import models as conference_models

from . import settings


class ProposalsMenu(CMSAttachMenu):
    name = _("Proposals menu")

    def get_nodes(self, request):
        nodes = []
        if request.user.is_authenticated():
            nodes.append(NavigationNode(
                _("My proposals"), reverse('my_proposals'), "proposals-mine"
                ))
            if settings.UNIFIED_SUBMISSION_FORM:
                nodes.append(NavigationNode(
                        _("Submit"), reverse('submit_proposal'), "proposals-submit"
                        ))
            else:
                for kind in conference_models.SessionKind.current_objects.all():
                    if kind.accepts_proposals():
                        nodes.append(NavigationNode(
                            _("Submit %s") % kind.name, reverse('typed_submit_proposal', kwargs={'type': kind.slug}), "proposals-submit-{0}".format(kind.pk)
                            ))
        return nodes

menu_pool.register_menu(ProposalsMenu)
