from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _

from .menu import ProposalsMenu


class ProposalsApp(CMSApp):
    name = _("Proposals app")
    urls = ["pyconde.proposals.urls"]
    menus = [ProposalsMenu]

apphook_pool.register(ProposalsApp)
