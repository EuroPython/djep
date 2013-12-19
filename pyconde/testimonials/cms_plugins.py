from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models


class CMSTestimonialPlugin(CMSPluginBase):
    model = models.TestimonialPlugin
    name = _('Testimonial')
    render_template = "testimonials/plugins/testimonial.html"

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'placeholder': placeholder,
        })
        return context


class CMSTestimonialCollectionPlugin(CMSPluginBase):
    model = models.TestimonialCollectionPlugin
    name = _('Testimonial collection')
    render_template = "testimonials/plugins/testimonial_collection.html"
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSTestimonialPlugin)
plugin_pool.register_plugin(CMSTestimonialCollectionPlugin)
