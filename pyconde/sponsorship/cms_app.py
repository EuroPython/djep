from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from pyconde.sponsorship.menu import SponsorshipMenu

class SponsorshipApp(CMSApp):
    name = _("Sponsorship App")
    urls = ["pyconde.sponsorship.urls"]
    menus = [SponsorshipMenu]

apphook_pool.register(SponsorshipApp)
