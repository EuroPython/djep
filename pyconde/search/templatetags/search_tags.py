from django import template
from django.db.models.loading import get_model

from .. import utils


register = template.Library()


@register.filter('has_fields')
def has_fields(facet):
    if not facet:
        return False
    for val in facet:
        if val[1] > 0:
            return True
    return False


@register.filter
def as_model_name(django_ct):
    model = get_model(*django_ct.split("."))
    return model._meta.verbose_name


@register.inclusion_tag('search/tags/show_facet.html', takes_context=True)
def show_facet(context, facet, title, facet_field):
    return {
        'title': title,
        'has_fields': has_fields(facet),
        'facet': facet,
        'facet_field': facet_field,
        'request': context['request']
        }


class FacetedSearchUrlNode(template.Node):
    def __init__(self, facet_name, facet_value):
        self.facet_name = facet_name
        self.facet_value = facet_value

    def render(self, context):
        fn = self.get_value(self.facet_name, context)
        fv = self.get_value(self.facet_value, context)
        return utils.set_facet_value(context['request'].get_full_path(), fn, fv)

    def get_value(self, var, context):
        if var.startswith(("'", '"')):
            return var[1:-1]
        else:
            return template.Variable(var).resolve(context)


@register.tag('faceted_search_url')
def do_faceted_search_url(parser, token):
    tag_name, facet_name, facet_value = token.split_contents()
    return FacetedSearchUrlNode(facet_name, facet_value)
