from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _

from .menu import AccountsMenu


class AccountsApp(CMSApp):
    """
    The AccountsApp allows to embed the whole accounts section into a cms page.
    """
    name = _("Accounts app")
    urls = ["pyconde.accounts.urls"]
    menus = [AccountsMenu]

apphook_pool.register(AccountsApp)
