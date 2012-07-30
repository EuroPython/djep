from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _


class ScheduleApp(CMSApp):
    name = _("Schedule app")
    urls = ["pyconde.schedule.urls"]

apphook_pool.register(ScheduleApp)
