from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _

from .menu import ScheduleMenu


class ScheduleApp(CMSApp):
    name = _("Schedule app")
    urls = ["pyconde.schedule.urls"]
    menus = [ScheduleMenu]

apphook_pool.register(ScheduleApp)
