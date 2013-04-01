from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models 

class SponsorListPlugin(CMSPluginBase):
    model = models.SponsorListPlugin
    name = _("sponsor list plugin")
    render_template = "cms/plugins/sponsorship/list.html"

    def render(self, context, instance, placeholder):
        levels = instance.levels.order_by('order').all()
        sponsors = models.Sponsor.objects.filter(
            level__in=levels).order_by('level__order').select_related('level')
        groups = None
        sublists = None
        if instance.group:
            groups = []
            current_level = None
            current_level_items = []
            for sponsor in sponsors:
                if current_level is None:
                    current_level = sponsor.level
                if current_level.pk is not sponsor.level.pk:
                    groups.append({'level': current_level, 'sponsors': current_level_items})
                    current_level = sponsor.level
                    current_level_items = []
                current_level_items.append(sponsor)
            if current_level_items:
                groups.append({'level': current_level, 'sponsors': current_level_items})
        elif instance.split_list_length is not None:
            sponsor_list = list(sponsors)
            sublists = [sponsor_list[i:i+instance.split_list_length] for i in range(0, len(sponsor_list), instance.split_list_length)]
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'sponsors': sponsors,
            'groups': groups,
            'sublists': sublists
            })
        return context

plugin_pool.register_plugin(SponsorListPlugin)
