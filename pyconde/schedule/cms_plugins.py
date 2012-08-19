from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import utils
from . import models


class CMSCompleteSchedulePlugin(CMSPluginBase):
    """
    Plugin for rendering the whole conference schedule.
    """
    model = models.CompleteSchedulePlugin
    name = _('Complete schedule')
    render_template = "schedule/plugins/complete.html"

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'schedule': utils.create_schedule(),
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSCompleteSchedulePlugin)
