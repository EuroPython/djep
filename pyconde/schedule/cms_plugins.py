from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models, utils


class CMSCompleteSchedulePlugin(CMSPluginBase):
    """
    Plugin for rendering the whole conference schedule.
    """
    model = models.CompleteSchedulePlugin
    name = _('Complete schedule')
    render_template = "schedule/plugins/complete.html"

    def render(self, context, instance, placeholder):
        schedule = utils.create_schedule(row_duration=instance.row_duration,
                                         merge_sections=instance.merge_sections)
        incl_sections = instance.sections.all()
        if not incl_sections:
            schedule = schedule
        else:
            s = SortedDict()
            for k, v in schedule.iteritems():
                if k in incl_sections:
                    s[k] = v
            schedule = s
        context.update({
            'instance': instance,
            'schedule': schedule,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSCompleteSchedulePlugin)
