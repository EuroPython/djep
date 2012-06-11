# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer


class AvatarWidget(forms.ClearableFileInput):
    """Widget for the avatar model field."""
    template_with_initial = u'%(initial)s<br />%(clear_template)s<br />%(input_text)s: %(input)s'

    def __init__(self, attrs=None, size=()):
        """Define the size of the thumbnail using the size kwarg tuple."""
        super(AvatarWidget, self).__init__(attrs)
        self.size = size

    def render(self, name, value, attrs=None):
        """Renders a thumbnail of the image with controls to clear/change it.

        If no image exists just an image upload widget is rendered.

        If an image has already been uploaded a thumbnail will be shown. The
        thumbnail's width and/or height are defined by the size kwarg given to
        the constructor. In addition a checkbox to delete the image is added.
        """
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(forms.ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, 'url'):
            template = self.template_with_initial
            initial = u'<a href="%(url)s"><img src="%(img_url)s" alt="%(alt)s" /></a>'
            thumbnail = get_thumbnailer(value).get_thumbnail(
                {'size': self.size})
            initial_substitutions = {
                'url': escape(value.url),
                'img_url': u'%s/%s' % (settings.MEDIA_URL, escape(thumbnail)),
                'alt': _(u'avatar')
            }
            substitutions['initial'] = initial % initial_substitutions
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = forms.CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
